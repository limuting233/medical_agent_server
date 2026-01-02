from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.graph.triage_nurse.prompt import TRIAGE_NURSE_SYSTEM_PROMPT
from app.graph.triage_nurse.schemas import TriageNurseOutput


class TriageNurseAgentBuilder:
    """
    分诊护士智能体构造类
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            base_url=settings.OPENAI_API_BASE,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
        )

    def build(self):
        """
        构建分诊护士智能体实例
        """
        return self.llm.with_structured_output(TriageNurseOutput)
