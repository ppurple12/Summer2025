from pydantic import BaseModel, Field

class ConflictMatrixCreate(BaseModel):
    AGENT_NUM_1: int = Field(..., alias="AGENT_NUM_1")
    AGENT_NUM_2: int = Field(..., alias="AGENT_NUM_2")
    CONFLICT_VALUE: float = Field(..., alias="CONFLICT_VALUE")

    model_config = {
        "validate_by_name": True
    }

class ConflictMatrixResponse(BaseModel):
    AGENT_NUM_1: int = Field(..., alias="AGENT_NUM_1")
    AGENT_NUM_2: int = Field(..., alias="AGENT_NUM_2")
    CONFLICT_VALUE: float = Field(..., alias="CONFLICT_VALUE")

    model_config = {
        "from_attributes": True
    }