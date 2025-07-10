from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from bson import ObjectId
import pandas as pd

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class RoleModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    role_name: str
    prompt: str
    requirements: List[str]
    positive_traits: List[str]
    negative_traits: List[str]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class AgentDocument(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    agent_num: int
    agent_id: int
    agent_name: str
    file_hash: str
    documents: Dict[str, List[Dict[str, Any]]]
    evaluation: Dict[str, int]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            pd.Timestamp: lambda v: v.isoformat()
        }