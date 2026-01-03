from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.graph.general_doctor.prompt import GENERAL_DOCTOR_SYSTEM_PROMPT


class GeneralDoctorAgentBuilder:
    """
    全科医生智能体构造类
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
        构造全科医生智能体实例
        """
        return create_agent(
            model=self.llm,
            tools=[],
            middleware=[],
            system_prompt=GENERAL_DOCTOR_SYSTEM_PROMPT,
            debug=True,
        )
