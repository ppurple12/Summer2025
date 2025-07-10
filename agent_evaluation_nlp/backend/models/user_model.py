from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.sql import Base
from models.conflict_matrix_model import Conflict_matrix

class User(Base):
    __tablename__ = "USERS"

    USER_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    FIRST_NAME = Column(String(50), nullable=False)
    LAST_NAME = Column(String(80), nullable=False)
    USER_EMAIL = Column(String(255), nullable=False, unique=True, index=True)
    USER_PASSWORD = Column(String(255), nullable=False)
    COMPANY_NAME = Column(String(255))
    COMPANY_DEPARTMENT = Column(String(255))
    COMPANY_POSITION = Column(String(255))

    agents = relationship("Agent", back_populates="user")
    roles = relationship("Role", back_populates="user", cascade="all, delete-orphan", single_parent=True) 
    role_ranges = relationship(
        "Role_range",
        back_populates="user",
        cascade="all, delete-orphan",
        single_parent=True  # ✅ required if using delete-orphan
    )
    agent_constraints = relationship("Agent_constraints", back_populates="user")
    conflict_matrices = relationship("Conflict_matrix", back_populates="user")