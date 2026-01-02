from langchain_core.messages import SystemMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from app.graph.general_doctor.agent import GeneralDoctorAgentBuilder
from app.graph.receptionist.agent import ReceptionistAgentBuilder
from app.graph.state import MedicalAgentState
from app.graph.triage_nurse.agent import TriageNurseAgentBuilder
from app.graph.triage_nurse.prompt import TRIAGE_NURSE_SYSTEM_PROMPT
from loguru import logger


async def triage_nurse_node(state: MedicalAgentState):
    """
    分诊护士节点
    """
    logger.info(f"进入triage_nurse_node")

    messages = state["messages"]  # 获取当前状态中的消息列表
    # last_msg = messages[-1]  # 获取消息列表中的最后一条消息
    # if isinstance(last_msg, AIMessage):
    #     logger.info(f"接下来进入节点: finish，原因: 最后一条消息是AIMessage")
    #     return {"next": "finish"}  # 更新state中的next字段
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
    logger.info(f"进入receptionist_node, 当前状态: {state}")
    receptionist_agent = ReceptionistAgentBuilder().build()  # 构建接待员智能体实例
    resp = await receptionist_agent.ainvoke({
        "messages": state["messages"],
    })
    return {
        "messages": resp["messages"][-1],
        "next": None
    }


def route_triage_nurse(state: MedicalAgentState) -> str:
    """
    分诊护士路由函数，根据状态中的 next 字段决定下一个节点
    """
    return state["next"]


def create_graph():
    """
    创建医疗智能体图
    """
    graph = StateGraph(MedicalAgentState)

    graph.add_node(triage_nurse_node, "triage_nurse_node")  # 添加分诊护士节点
    graph.add_node(general_doctor_node, "general_doctor_node")  # 添加全科医生节点
    graph.add_node(receptionist_node, "receptionist_node")  # 添加接待员节点

    graph.add_edge(START, "triage_nurse_node")  # 添加从START到分诊护士节点的边

    graph.add_conditional_edges(
        "triage_nurse_node",
        route_triage_nurse,
        {
            "general_doctor_node": "general_doctor_node",  # 医疗问诊 -> 全科医生
            "receptionist_node": "receptionist_node",  # 非医疗咨询 -> 接待员
            "finish": END,  # 结束对话
        }
    )

    graph.add_edge("general_doctor_node", END)  # 添加从全科医生节点到结束节点的边
    graph.add_edge("receptionist_node", END)  # 添加从接待员节点到结束节点的边

    return graph.compile(checkpointer=InMemorySaver())
