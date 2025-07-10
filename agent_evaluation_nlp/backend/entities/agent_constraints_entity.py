from pydantic import BaseModel, Field
from typing import List, Optional

class AgentConstraintCreate(BaseModel):
    AGENT_NUM: int
    MAX_ROLES: int

class AgentConstraintResponse(BaseModel):
    AGENT_NUM: int
    MAX_ROLES: int

