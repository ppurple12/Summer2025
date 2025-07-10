from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.sql import Base

# agent entity to be used to add to the SQL table
class Role(Base):
    __tablename__ = "ROLES_PER_USER"

    ROLE_NAME = Column(String(255), primary_key=True)
    USER_ID = Column(Integer, ForeignKey("USERS.USER_ID", ondelete="CASCADE"))
    ROLE_KEYWORD = Column(String(255), primary_key=True)
    DEFINING_WORD = Column(String(255))

    
    user = relationship("User", back_populates="roles")