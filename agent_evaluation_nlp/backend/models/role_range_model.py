from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.sql import Base

class Role_range(Base):
    __tablename__ = "ROLE_RANGE"

    USER_ID = Column(Integer, ForeignKey("USERS.USER_ID", ondelete="CASCADE"), primary_key=True)
    DEFINING_WORD = Column(String(255), primary_key=True)

    REQUIRED_AGENTS = Column(Integer, nullable=False, default=0)
    MULTI = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="role_ranges", foreign_keys=[USER_ID])