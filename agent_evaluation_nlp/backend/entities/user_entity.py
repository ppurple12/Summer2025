from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    FIRST_NAME: str
    LAST_NAME: str
    USER_EMAIL: EmailStr
    USER_PASSWORD: str
    COMPANY_NAME: str | None = None
    COMPANY_DEPARTMENT: str | None = None
 

class UserResponse(BaseModel):
    USER_ID: int
    FIRST_NAME: str
    LAST_NAME: str
    USER_EMAIL: EmailStr
    COMPANY_NAME: str | None
    COMPANY_DEPARTMENT: str | None
    
    model_config = {
        "from_attributes": True
    }

class LoginRequest(BaseModel):
    USER_EMAIL: EmailStr
    USER_PASSWORD: str