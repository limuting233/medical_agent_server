from typing import Literal

from pydantic import BaseModel, Field


class TriageNurseOutput(BaseModel):
    """
    分诊护士结构化输出模型
    """
    next: Literal["general_doctor_node", "receptionist_node", "finish"] = Field(
        description="下一步流转节点：general_doctor_node（问诊医生节点）、receptionist_node（前台接待员节点）、finish（结束）"
    )
    reason: str = Field(description="选择该流转节点的原因（简要说明）")
