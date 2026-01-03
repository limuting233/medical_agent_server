from langchain.agents import AgentState


class MedicalAgentState(AgentState):
    """
    定义医疗智能体的状态结构，继承自 AgentState。
    """
    # user_id 和session_id是多对一关系，一个user_id可以对应多个session_id，一个session_id只能对应一个user_id
    user_id: str  # 用户 ID，一个user_id唯一标识一个用户
    # session_id: str  # 会话 ID，一个session_id唯一标识一个用户会话
    next: str  # next 字段用于在图的边中决定下一个去哪里
