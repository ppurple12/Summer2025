from pydantic import BaseModel, Field
from typing import List, Optional

# models for frontend to use 
class AgentCreate(BaseModel):
    AGENT_ID: Optional[int] = Field(None, alias="AGENT_ID")
    FIRST_NAME: str = Field(..., alias="FIRST_NAME")
    LAST_NAME: str = Field(..., alias="LAST_NAME")

    class Config:
        validate_by_name = True

class AgentResponse(BaseModel):
    FIRST_NAME: Optional[str] = Field(None, alias="FIRST_NAME")
    LAST_NAME: str = Field(..., alias="LAST_NAME")
    AGENT_NUM: int = Field(..., alias="AGENT_NUM")
    AGENT_ID: Optional[int] = Field(..., alias="AGENT_ID")
    model_config = {
        "from_attributes": True
    }
