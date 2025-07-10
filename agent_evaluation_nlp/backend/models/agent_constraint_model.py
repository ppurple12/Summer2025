from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.sql import Base  # adjust if your Base is defined elsewhere

class Agent_constraints(Base):
    __tablename__ = "AGENT_CONSTRAINTS"

    USER_ID = Column(Integer, ForeignKey("USERS.USER_ID",  ondelete='CASCADE'), primary_key=True)
    AGENT_NUM = Column(Integer, ForeignKey("AGENTS.AGENT_NUM",  ondelete='CASCADE'), primary_key=True)
    MAX_ROLES = Column(Integer, nullable=False)

    # Optional: relationships (if you want access to agent or user objects)
    user = relationship("User", back_populates="agent_constraints")
    agent = relationship("Agent", back_populates="constraints")