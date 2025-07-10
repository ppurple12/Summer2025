from pydantic import BaseModel, Field
from typing import List, Optional

class RoleRangeCreate(BaseModel):
    DEFINING_WORD: str
    REQUIRED_AGENTS: int

class RoleRangeResponse(BaseModel):
    DEFINING_WORD: str
    REQUIRED_AGENTS: int

