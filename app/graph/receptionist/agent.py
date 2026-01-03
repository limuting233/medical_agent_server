from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.graph.receptionist.prompt import RECEPTIONIST_SYSTEM_PROMPT


class ReceptionistAgentBuilder:
    """
    接待员智能体构造类
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
        构建接待员智能体实例
        """
        return create_agent(
            model=self.llm,
            system_prompt=RECEPTIONIST_SYSTEM_PROMPT,
            tools=[],
            middleware=[],
            debug=True,
        )
