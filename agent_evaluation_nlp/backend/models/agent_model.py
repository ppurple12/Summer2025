from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.sql import Base
from models.conflict_matrix_model import Conflict_matrix

class Agent(Base):
    __tablename__ = "AGENTS"

    AGENT_NUM = Column(Integer, primary_key=True)
    AGENT_ID = Column(Integer)
    USER_ID = Column(Integer, ForeignKey("USERS.USER_ID"))
    FIRST_NAME = Column(String(50), nullable=False)
    LAST_NAME = Column(String(80), nullable=False)

    user = relationship("User", back_populates="agents")
    constraints = relationship("Agent_constraints", back_populates="agent", cascade="all, delete-orphan")

    conflict_agent_1 = relationship(
        "Conflict_matrix",
        back_populates="agent_1",
        foreign_keys=[Conflict_matrix.AGENT_NUM_1],
         cascade="all, delete-orphan"
    )

    conflict_agent_2 = relationship(
        "Conflict_matrix",
        back_populates="agent_2",
        foreign_keys=[Conflict_matrix.AGENT_NUM_2],
         cascade="all, delete-orphan"
    )