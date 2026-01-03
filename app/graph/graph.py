from langchain_core.messages import SystemMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.store.postgres import AsyncPostgresStore

from app.core.config import settings
from app.graph.general_doctor.agent import GeneralDoctorAgentBuilder
from app.graph.receptionist.agent import ReceptionistAgentBuilder
from app.graph.state import MedicalAgentState
from app.graph.triage_nurse.agent import TriageNurseAgentBuilder
from app.graph.triage_nurse.prompt import TRIAGE_NURSE_SYSTEM_PROMPT
from loguru import logger

checkpointer: AsyncPostgresSaver | None = None  # 定义异步Postgres短期记忆保存器
_checkpointer_context = None
store: AsyncPostgresStore | None = None  # 定义异步Postgres长期记忆存储
_store_context = None


async def init_checkpointer():
    """
    初始化 PostgreSQL checkpointer 短期记忆
    """
    logger.info(f"正在初始化 PostgreSQL checkpointer 短期记忆 ...")
    global checkpointer, _checkpointer_context
    _checkpointer_context = AsyncPostgresSaver.from_conn_string(conn_string=settings.DB_URL)
    checkpointer = await _checkpointer_context.__aenter__()
    await checkpointer.setup()
    logger.info(f"PostgreSQL checkpointer 短期记忆 初始化完成")


async def close_checkpointer():
    """
    关闭 PostgreSQL checkpointer 短期记忆 连接
    """
    logger.info(f"正在关闭 PostgreSQL checkpointer 短期记忆 ...")
    global checkpointer, _checkpointer_context
    if checkpointer is not None and _checkpointer_context is not None:
        await _checkpointer_context.__aexit__(None, None, None)
        checkpointer = None
        _checkpointer_context = None
    logger.info(f"PostgreSQL checkpointer 短期记忆 连接已关闭")


async def init_store():
    """
    初始化 PostgreSQL store 长期记忆
    """
    logger.info("正在初始化 PostgreSQL store 长期记忆 ...")
    global store, _store_context
    _store_context = AsyncPostgresStore.from_conn_string(conn_string=settings.DB_URL)
    store = await _store_context.__aenter__()
    await store.setup()
    logger.info(f"PostgreSQL store 长期记忆 初始化完成")


async def close_store():
    """
    关闭 PostgreSQL store 长期记忆 连接
    """
    logger.info(f"正在关闭 PostgreSQL store 长期记忆 ...")
    global store, _store_context
    if store is not None and _store_context is not None:
        await _store_context.__aexit__(None, None, None)
        store = None
        _store_context = None
    logger.info(f"PostgreSQL store 长期记忆 连接已关闭")


async def triage_nurse_node(state: MedicalAgentState):
    """
    分诊护士节点
    """
    logger.info(f"进入triage_nurse_node")

    messages = state["messages"]  # 获取当前状态中的消息列表
    triage_nurse_agent = TriageNurseAgentBuilder().build()  # 构建分诊护士智能体实例
    resp = await triage_nurse_agent.ainvoke(
        [SystemMessage(content=TRIAGE_NURSE_SYSTEM_PROMPT)] + messages)  # 调用分诊护士智能体，传入系统提示和消息列表
    logger.info(f"接下来进入节点: {resp.next}，原因: {resp.reason}")
    return {"next": resp.next}  # 更新state中的next字段


async def general_doctor_node(state: MedicalAgentState):
    """
    全科医生节点
    """
    logger.info(f"进入general_doctor_node")
    general_doctor_agent = GeneralDoctorAgentBuilder().build()  # 构建全科医生智能体实例
    resp = await general_doctor_agent.ainvoke({
        "messages": state["messages"],
    })
    return {
        "messages": resp["messages"][-1],
        "next": None
    }


async def receptionist_node(state: MedicalAgentState):
    """
    接待员节点
    """
    logger.info(f"进入receptionist_node")
    receptionist_agent = ReceptionistAgentBuilder().build()  # 构建接待员智能体实例
    resp = await receptionist_agent.ainvoke({
        "messages": state["messages"],
    })
    return {
        "messages": resp["messages"][-1],
        "next": None
    }


# def route_triage_nurse(state: MedicalAgentState) -> str:
#     """
#     分诊护士路由函数，根据状态中的 next 字段决定下一个节点
#     """
#     return state["next"]


def create_graph():
    """
    创建医疗智能体图
    """
    if checkpointer is None:
        raise RuntimeError("Checkpointer 未初始化")
    graph = StateGraph(state_schema=MedicalAgentState)

    graph.add_node(triage_nurse_node, "triage_nurse_node")  # 添加分诊护士节点
    graph.add_node(general_doctor_node, "general_doctor_node")  # 添加全科医生节点
    graph.add_node(receptionist_node, "receptionist_node")  # 添加接待员节点

    graph.add_edge(START, "triage_nurse_node")  # 添加从START到分诊护士节点的边

    graph.add_conditional_edges(
        "triage_nurse_node",
        lambda state: state["next"],
        {
            "general_doctor_node": "general_doctor_node",  # 医疗问诊 -> 全科医生
            "receptionist_node": "receptionist_node",  # 非医疗咨询 -> 接待员
            "finish": END,  # 结束对话
        }
    )

    graph.add_edge("general_doctor_node", END)  # 添加从全科医生节点到结束节点的边
    graph.add_edge("receptionist_node", END)  # 添加从接待员节点到结束节点的边

    return graph.compile(checkpointer=checkpointer, store=store)
