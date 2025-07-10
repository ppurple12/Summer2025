from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.sql import get_db
from models.agent_model import Agent
from motor.motor_asyncio import AsyncIOMotorCollection
from entities.agent_entity import AgentResponse, AgentCreate
from typing import List
from database.mongo import get_documents_collection
from models.role_model import Role

router = APIRouter()

# gets all agents for the specified userID (manager) and returns a list of them
@router.get("/agents/{user_id}", response_model=List[AgentResponse])
def get_agents(user_id: int, db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    return agents


# gets the new agent entity and adds it to SQL db
@router.post("/agents/{user_id}", response_model=AgentResponse)
async def create_agent(user_id: int, agent: AgentCreate, db: Session = Depends(get_db),
                 docs_collection: AsyncIOMotorCollection = Depends(get_documents_collection)):
    # add agent to sql
    db_agent = Agent(**agent.dict(by_alias=False)) 
    db_agent.USER_ID = user_id 
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    roles = db.query(Role).filter(Role.USER_ID == user_id).all()
    agent = db.query(Agent).filter(Agent.USER_ID == user_id).order_by(Agent.AGENT_NUM.desc()).first() #get latest agent

    # add agent to mongo
    # Insert the entire document if it's a new agent
    agent_abilities = {}
    agent_name = agent.FIRST_NAME + " " + agent.LAST_NAME

    for role in roles:
        agent_abilities[role.DEFINING_WORD] = 0  
    await docs_collection.insert_one({
        "user_id": user_id,
        "agent_id": agent.AGENT_ID,
        "agent_num": agent.AGENT_NUM,
        "agent_name": agent_name,
        "documents": {},
        "evaluation": agent_abilities
    })
    return db_agent


# deletes a specified agent given an agentID and userID 
@router.delete("/agents/{agent_num}")
async def delete_agent(
    agent_num: int,
    db: Session = Depends(get_db),
    docs_collection: AsyncIOMotorCollection = Depends(get_documents_collection)
):
    # Fetch agent from SQL
    agent = db.query(Agent).filter(Agent.AGENT_NUM == agent_num).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    user_id = agent.USER_ID  # Save before deleting

    # Delete agent from SQL
    db.delete(agent)
    db.commit()

    # Delete related MongoDB documents
    delete_result = await docs_collection.delete_many({
        "agent_num": agent_num,
    })

    return {
        "message": f"Agent {agent_num} removed successfully",
        "mongo_deleted_count": delete_result.deleted_count
    }