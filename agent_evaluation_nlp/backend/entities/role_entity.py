from pydantic import BaseModel, Field
from typing import List, Optional

class RoleCreate(BaseModel):
    ROLE_NAME: str
    ROLE_KEYWORDS: Optional[List[str]] = None

class RoleResponse(BaseModel):
    ROLE_NAME: str
    ROLE_KEYWORD: Optional[str] = None

class KeywordCreate(BaseModel):
    ROLE_NAME: str
    ROLE_KEYWORD: str