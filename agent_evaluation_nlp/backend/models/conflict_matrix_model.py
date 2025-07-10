from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.sql import Base

class Conflict_matrix(Base):
    __tablename__ = "CONFLICT_MATRIX"

    USER_ID = Column(Integer, ForeignKey("USERS.USER_ID"), primary_key=True)
    AGENT_NUM_1 = Column(Integer, ForeignKey("AGENTS.AGENT_NUM",  ondelete='CASCADE'), primary_key=True)
    AGENT_NUM_2 = Column(Integer, ForeignKey("AGENTS.AGENT_NUM",  ondelete='CASCADE'), primary_key=True)
    CONFLICT_VALUE = Column(Float, nullable=False)
    COOPERATION = Column(Boolean, default=True)

    user = relationship("User", back_populates="conflict_matrices")
    agent_1 = relationship("Agent", foreign_keys=[AGENT_NUM_1], back_populates="conflict_agent_1")
    agent_2 = relationship("Agent", foreign_keys=[AGENT_NUM_2], back_populates="conflict_agent_2")