from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.sql import get_db
from sqlalchemy import func
from models.agent_model import Agent
from models.role_model import Role
from typing import List

from database.mongo import get_documents_collection
from motor.motor_asyncio import AsyncIOMotorCollection
from services.gra_services import GRA, GMRA, GRACCF, GMRACCF
from fastapi import Query, HTTPException
from typing import Optional
from models.user_model import User
from models.role_range_model import Role_range
from entities.role_range_entity import RoleRangeCreate
from models.agent_constraint_model import Agent_constraints
from entities.agent_constraints_entity import AgentConstraintCreate
from models.conflict_matrix_model import Conflict_matrix
import json
import urllib.parse

router = APIRouter()

############################
#       GRA REQUESTS       #
############################
@router.get("/GRA_1/{user_id}")
async def get_gra_assignment_matrix(
    user_id: int,
    db: Session = Depends(get_db)
):
    agents = [a[0] for a in db.query(Agent.AGENT_NUM).filter(Agent.USER_ID == user_id).distinct().all()]
    roles = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()

    role_rows = [
        {
            "role": role.ROLE_NAME,
            "defining_word": role.DEFINING_WORD,
            "required_agents": 0
        }
        for role in roles
    ]
    
    return {
        "agents": agents,
        "roles": role_rows
    }

@router.post("/GRA/roles/{user_id}")
def submit_role_assignments(
    user_id: int,
    payload: List[RoleRangeCreate],
    db: Session = Depends(get_db)
):
    
    print("Received roles:", payload)
    for role in payload:
        db.query(Role_range).filter(
            Role_range.USER_ID == user_id,
            Role_range.MULTI == False
        ).delete()

        db.add(Role_range(
            USER_ID=user_id,
            DEFINING_WORD=role.DEFINING_WORD,
            REQUIRED_AGENTS=role.REQUIRED_AGENTS,
            MULTI=False
        ))

    db.commit()
    
@router.get("/GRA/matrix/{user_id}")
async def get_assignment_matrix_GRA(
    user_id: int,
    db: Session = Depends(get_db),
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)
):
    user = db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    roles_raw = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    if not roles_raw:
        raise HTTPException(status_code=404, detail="No roles found")

    # Convert roles to dicts for clarity
    roles = [{"ROLE_NAME": r[0], "DEFINING_WORD": r[1]} for r in roles_raw]

    assignments = db.query(Role_range.DEFINING_WORD, Role_range.REQUIRED_AGENTS) \
    .filter(Role_range.USER_ID == user_id, Role_range.MULTI == False).all()

    assignment_map = {def_word: count for def_word, count in assignments}

    L = [assignment_map.get(role["DEFINING_WORD"], 0) for role in roles]

    # Fetch documents from MongoDB
    documents_cursor = doc_collection.find({"user_id": user_id})
    documents = await documents_cursor.to_list(length=None)

    # Build evaluation dict
    evaluations = {}
    for doc in documents:
        agent_num = doc.get("agent_num")
        eval_data = doc.get("evaluation", {})
        evaluations[agent_num] = {
            role["ROLE_NAME"]: eval_data.get(role["DEFINING_WORD"], 0)
            for role in roles
        }

    # Build matrix: rows = agents, columns = role scores
    matrix = [
        [evaluations.get(agent.AGENT_NUM, {}).get(role["ROLE_NAME"], 0) for role in roles]
        for agent in agents
    ]
    assignment_matrix = GRA(matrix, L)
    print(assignment_matrix)
    return {
        "agents": [
            {
                "AGENT_NUM": a.AGENT_NUM,
                "FIRST_NAME": a.FIRST_NAME,
                "LAST_NAME": a.LAST_NAME
            } for a in agents
        ],
        "roles": roles,
        "evaluations": evaluations,
        "matrix": assignment_matrix,
        "user": {
            "COMPANY_NAME": user.COMPANY_NAME,
            "DEPARTMENT": user.COMPANY_DEPARTMENT
        }
    }


############################
#       GMRA REQUESTS       #
############################
@router.get("/GMRA_1/{user_id}")
async def get_gmra_assignment_matrix(
    user_id: int,
    db: Session = Depends(get_db)
):
    agents = [a[0] for a in db.query(Agent.AGENT_NUM).filter(Agent.USER_ID == user_id).distinct().all()]
    roles = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()

    role_rows = [
        {
            "role": role.ROLE_NAME,
            "defining_word": role.DEFINING_WORD,
            "required_agents": 0
        }
        for role in roles
    ]
    
    return {
        "agents": agents,
        "roles": role_rows
    }

@router.post("/GMRA/agents/{user_id}")
def submit_role_assignments(
    user_id: int,
    payload: List[RoleRangeCreate],
    db: Session = Depends(get_db)
):
    
    print("Received roles:", payload)
    for role in payload:
        db.query(Role_range).filter(
            Role_range.USER_ID == user_id,
            Role_range.MULTI == True
        ).delete()

        db.add(Role_range(
            USER_ID=user_id,
            DEFINING_WORD=role.DEFINING_WORD,
            REQUIRED_AGENTS=role.REQUIRED_AGENTS,
            MULTI=True
        ))

    db.commit()

@router.get("/GMRA_2/{user_id}")
async def get_gmra_assignment_matrix(
    user_id: int,
    db: Session = Depends(get_db)
):
    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    roles = [r[0] for r in db.query(Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()]
    amount = db.query(func.sum(Role_range.REQUIRED_AGENTS))\
                        .filter(Role_range.USER_ID == user_id, Role_range.MULTI == True)\
                        .scalar() or 0  # ensures None becomes 0

    return {
        "agents": agents,
        "roles": roles,
        "amount": amount
    }

@router.post("/GMRA_2/agents/{user_id}")
def submit_role_assignments(
    user_id: int,
    payload: List[AgentConstraintCreate],
    db: Session = Depends(get_db)
):
    
    print("Received roles:", payload)
    for agent in payload:
        existing = db.query(Agent_constraints).filter(
            Agent_constraints.USER_ID == user_id,
            Agent_constraints.AGENT_NUM == agent.AGENT_NUM
        ).first()

        if existing:
            existing.MAX_ROLES = agent.MAX_ROLES
        else:
            db.add(Agent_constraints(
                USER_ID=user_id,
                AGENT_NUM=agent.AGENT_NUM,
                MAX_ROLES=agent.MAX_ROLES
            ))

    db.commit()


@router.get("/GMRA/matrix/{user_id}")
async def get_assignment_matrix_GMRA(
    user_id: int,
    db: Session = Depends(get_db),
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)
):
    user = db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    roles_raw = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    if not roles_raw:
        raise HTTPException(status_code=404, detail="No roles found")

    # Convert roles to dicts for clarity
    roles = [{"ROLE_NAME": r[0], "DEFINING_WORD": r[1]} for r in roles_raw]
    
    r_assignments = db.query(Role_range.DEFINING_WORD, Role_range.REQUIRED_AGENTS) \
    .filter(Role_range.USER_ID == user_id, Role_range.MULTI == True).all()
    r_assignment_map = {def_word: count for def_word, count in r_assignments}
    L = [r_assignment_map.get(role["DEFINING_WORD"], 0) for role in roles]

    a_assignments = db.query(Agent_constraints.AGENT_NUM, Agent_constraints.MAX_ROLES) \
    .filter(Agent_constraints.USER_ID == user_id).all()
    a_assignment_map = {agent_num: count for agent_num, count in a_assignments}
    La = [a_assignment_map.get(agent.AGENT_NUM, 0) for agent in agents]

    # Fetch documents from MongoDB
    documents_cursor = doc_collection.find({"user_id": user_id})
    documents = await documents_cursor.to_list(length=None)

    # Build evaluation dict
    evaluations = {}
    for doc in documents:
        agent_num = doc.get("agent_num")
        eval_data = doc.get("evaluation", {})
        evaluations[agent_num] = {
            role["ROLE_NAME"]: eval_data.get(role["DEFINING_WORD"], 0)
            for role in roles
        }

    # Build matrix: rows = agents, columns = role scores
    matrix = [
        [evaluations.get(agent.AGENT_NUM, {}).get(role["ROLE_NAME"], 0) for role in roles]
        for agent in agents
    ]
    assignment_matrix = GMRA(matrix, L, La)
    print(assignment_matrix)
    return {
        "agents": [
            {
                "AGENT_NUM": a.AGENT_NUM,
                "FIRST_NAME": a.FIRST_NAME,
                "LAST_NAME": a.LAST_NAME
            } for a in agents
        ],
        "roles": roles,
        "evaluations": evaluations,
        "matrix": assignment_matrix,
        "user": {
            "COMPANY_NAME": user.COMPANY_NAME,
            "DEPARTMENT": user.COMPANY_DEPARTMENT
        }
    }
#################################
#           Conflict            #
#################################
@router.get("/conflicts/{user_id}")
def check_conflict_matrix(user_id: int, db: Session = Depends(get_db)):
      # Query for cooperation entries
    coop_entries = db.query(Conflict_matrix).filter(
        Conflict_matrix.USER_ID == user_id,
        Conflict_matrix.COOPERATION == True
    ).all()

    # Query for conflict entries
    conflict_entries = db.query(Conflict_matrix).filter(
        Conflict_matrix.USER_ID == user_id,
        Conflict_matrix.COOPERATION == False
    ).all()

    # If both are empty, raise 404
    if not coop_entries and not conflict_entries:
        raise HTTPException(status_code=404, detail="No conflict matrix found for this user")

    has_cooperation = any(coop_entries)
    has_conflict = any(conflict_entries)

    return {
        "has_conflict": has_conflict,
        "has_cooperation": has_cooperation
    }

@router.get("/agents_with_conflicts/{user_id}")
def get_agents_and_conflicts(
    user_id: int,
    mode: str = Query("gradient"),  # accepts ?mode=gradient or ?mode=binary
    db: Session = Depends(get_db)
):
    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    if not agents:
        raise HTTPException(status_code=404, detail="No agents found for user")

    # Determine COOPERATION flag based on mode
    is_cooperation = mode == "gradient"

    conflicts = db.query(Conflict_matrix).filter(
        Conflict_matrix.USER_ID == user_id,
        Conflict_matrix.COOPERATION == is_cooperation
    ).all()

    return {
        "agents": [
            {
                "AGENT_NUM": a.AGENT_NUM,
                "FIRST_NAME": a.FIRST_NAME,
                "LAST_NAME": a.LAST_NAME
            } for a in agents
        ],
        "conflicts": [
            {
                "AGENT_NUM_1": c.AGENT_NUM_1,
                "AGENT_NUM_2": c.AGENT_NUM_2,
                "CONFLICT_VALUE": c.CONFLICT_VALUE
            } for c in conflicts
        ]
    }

@router.post("/conflicts/{user_id}")
def submit_conflicts(user_id: int, payload: dict, db: Session = Depends(get_db)):
    conflicts = payload.get("conflicts", [])
    mode = payload.get("mode", "gradient")

    is_cooperation = mode == "gradient"

    db.query(Conflict_matrix).filter(
        Conflict_matrix.USER_ID == user_id,
        Conflict_matrix.COOPERATION == is_cooperation
    ).delete()

    for conflict in conflicts:
        db_conflict = Conflict_matrix(
            USER_ID=user_id,
            AGENT_NUM_1=conflict["AGENT_NUM_1"],
            AGENT_NUM_2=conflict["AGENT_NUM_2"],
            CONFLICT_VALUE=conflict["CONFLICT_VALUE"],
            COOPERATION=is_cooperation
        )
        db.add(db_conflict)

    db.commit()
    return {"message": "Conflicts submitted", "mode": mode}


@router.post("/GRA/consider_constraints/{user_id}")
async def consider_conflicts(    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)
):
    user = db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    roles_raw = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    if not roles_raw:
        raise HTTPException(status_code=404, detail="No roles found")
    
    agent_index = {agent.AGENT_NUM: idx for idx, agent in enumerate(agents)}
    
    # Convert roles to dicts for clarity
    roles = [{"ROLE_NAME": r[0], "DEFINING_WORD": r[1]} for r in roles_raw]

    assignments = db.query(Role_range.DEFINING_WORD, Role_range.REQUIRED_AGENTS) \
    .filter(Role_range.USER_ID == user_id, Role_range.MULTI == False).all()

    assignment_map = {def_word: count for def_word, count in assignments}

    L = [assignment_map.get(role["DEFINING_WORD"], 0) for role in roles]

    # Fetch documents from MongoDB
    documents_cursor = doc_collection.find({"user_id": user_id})
    documents = await documents_cursor.to_list(length=None)

    # Build evaluation dict
    evaluations = {}
    for doc in documents:
        agent_num = doc.get("agent_num")
        eval_data = doc.get("evaluation", {})
        evaluations[agent_num] = {
            role["ROLE_NAME"]: eval_data.get(role["DEFINING_WORD"], 0)
            for role in roles
        }

    # Build matrix: rows = agents, columns = role scores
    matrix = [
        [evaluations.get(agent.AGENT_NUM, {}).get(role["ROLE_NAME"], 0) for role in roles]
        for agent in agents
    ]

    cooperation = payload.get("cooperation", False)
    conflict_entries = db.query(Conflict_matrix).filter(Conflict_matrix.USER_ID == user_id, Conflict_matrix.COOPERATION == cooperation).all()
    conflict_pairs = {(c.AGENT_NUM_1, c.AGENT_NUM_2) for c in conflict_entries}
    conflict_pairs |= {(b, a) for (a, b) in conflict_pairs}  # ensure symmetry

    conflict_matrix = [[0] * len(agents) for _ in range(len(agents))]

    for a1, a2 in conflict_pairs:
        i = agent_index.get(a1)
        j = agent_index.get(a2)
        if i is not None and j is not None:
            conflict_matrix[i][j] = 1

    if (cooperation):
        assignment_matrix = GRACCF(matrix, L, conflict_matrix)
    else:
        assignment_matrix = GRA(matrix, L, conflict_matrix)
    return {
        "matrix": assignment_matrix,
        
    }

@router.post("/GMRA/consider_constraints/{user_id}")
async def gmra_with_conflicts(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)
):
    
    user = db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    if not agents:
        raise HTTPException(status_code=404, detail="No agents found")

    agent_index = {agent.AGENT_NUM: idx for idx, agent in enumerate(agents)}

  
    roles_raw = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    if not roles_raw:
        raise HTTPException(status_code=404, detail="No roles found")

    roles = [{"ROLE_NAME": r[0], "DEFINING_WORD": r[1]} for r in roles_raw]

    # make L
    r_assignments = db.query(Role_range.DEFINING_WORD, Role_range.REQUIRED_AGENTS) \
                      .filter(Role_range.USER_ID == user_id, Role_range.MULTI == True).all()
    r_assignment_map = {def_word: count for def_word, count in r_assignments}
    L = [r_assignment_map.get(role["DEFINING_WORD"], 0) for role in roles]

    # make La
    a_assignments = db.query(Agent_constraints.AGENT_NUM, Agent_constraints.MAX_ROLES) \
                      .filter(Agent_constraints.USER_ID == user_id).all()
    a_assignment_map = {agent_num: count for agent_num, count in a_assignments}
    La = [a_assignment_map.get(agent.AGENT_NUM, 0) for agent in agents]

    documents_cursor = doc_collection.find({"user_id": user_id})
    documents = await documents_cursor.to_list(length=None)

    evaluations = {}
    for doc in documents:
        agent_num = doc.get("agent_num")
        eval_data = doc.get("evaluation", {})
        evaluations[agent_num] = {
            role["ROLE_NAME"]: eval_data.get(role["DEFINING_WORD"], 0)
            for role in roles
        }

    # Step 7: Build score matrix
    matrix = [
        [evaluations.get(agent.AGENT_NUM, {}).get(role["ROLE_NAME"], 0) for role in roles]
        for agent in agents
    ]

    cooperation = payload.get("cooperation", False)
    conflict_entries = db.query(Conflict_matrix).filter(Conflict_matrix.USER_ID == user_id, Conflict_matrix.COOPERATION == cooperation).all()
    conflict_pairs = {(c.AGENT_NUM_1, c.AGENT_NUM_2) for c in conflict_entries}
    conflict_pairs |= {(b, a) for (a, b) in conflict_pairs}  # ensure symmetry

    conflict_matrix = [[0] * len(agents) for _ in range(len(agents))]

    for a1, a2 in conflict_pairs:
        i = agent_index.get(a1)
        j = agent_index.get(a2)
        if i is not None and j is not None:
            conflict_matrix[i][j] = 1

    
    if (cooperation):
        assignment_matrix = GMRACCF(matrix, L, La, conflict_matrix)
    else:
        assignment_matrix = GMRA(matrix, L, La, conflict_matrix)

    
    return {
        "matrix": assignment_matrix,
    }

@router.post("/GRA/consider_cooperation/{user_id}")
async def consider_conflicts(    user_id: int,
    db: Session = Depends(get_db),
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)
):
    user = db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    roles_raw = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    if not roles_raw:
        raise HTTPException(status_code=404, detail="No roles found")
    
    agent_index = {agent.AGENT_NUM: idx for idx, agent in enumerate(agents)}
    
    # Convert roles to dicts for clarity
    roles = [{"ROLE_NAME": r[0], "DEFINING_WORD": r[1]} for r in roles_raw]

    assignments = db.query(Role_range.DEFINING_WORD, Role_range.REQUIRED_AGENTS) \
    .filter(Role_range.USER_ID == user_id, Role_range.MULTI == False).all()

    assignment_map = {def_word: count for def_word, count in assignments}

    L = [assignment_map.get(role["DEFINING_WORD"], 0) for role in roles]

    # Fetch documents from MongoDB
    documents_cursor = doc_collection.find({"user_id": user_id})
    documents = await documents_cursor.to_list(length=None)

    # Build evaluation dict
    evaluations = {}
    for doc in documents:
        agent_num = doc.get("agent_num")
        eval_data = doc.get("evaluation", {})
        evaluations[agent_num] = {
            role["ROLE_NAME"]: eval_data.get(role["DEFINING_WORD"], 0)
            for role in roles
        }

    # Build matrix: rows = agents, columns = role scores
    matrix = [
        [evaluations.get(agent.AGENT_NUM, {}).get(role["ROLE_NAME"], 0) for role in roles]
        for agent in agents
    ]

    
    conflict_entries = db.query(Conflict_matrix).filter(Conflict_matrix.USER_ID == user_id).all()
    conflict_matrix = [[0] * len(agents) for _ in range(len(agents))]

    for c in conflict_entries:
        i = agent_index.get(c.AGENT_NUM_1)
        j = agent_index.get(c.AGENT_NUM_2)
        if i is not None and j is not None:
            conflict_matrix[i][j] = c.CONFLICT_VALUE
            conflict_matrix[j][i] = c.CONFLICT_VALUE 
    print(conflict_matrix)

    assignment_matrix = GRACCF(matrix, L, conflict_matrix)
    return {
        "matrix": assignment_matrix,
        
    }

@router.post("/GMRA/consider_cooperation/{user_id}")
async def gmra_with_conflicts(
    user_id: int,
    db: Session = Depends(get_db),
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)
):
    
    user = db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    if not agents:
        raise HTTPException(status_code=404, detail="No agents found")

    agent_index = {agent.AGENT_NUM: idx for idx, agent in enumerate(agents)}

  
    roles_raw = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    if not roles_raw:
        raise HTTPException(status_code=404, detail="No roles found")

    roles = [{"ROLE_NAME": r[0], "DEFINING_WORD": r[1]} for r in roles_raw]

    # make L
    r_assignments = db.query(Role_range.DEFINING_WORD, Role_range.REQUIRED_AGENTS) \
                      .filter(Role_range.USER_ID == user_id, Role_range.MULTI == True).all()
    r_assignment_map = {def_word: count for def_word, count in r_assignments}
    L = [r_assignment_map.get(role["DEFINING_WORD"], 0) for role in roles]

    # make La
    a_assignments = db.query(Agent_constraints.AGENT_NUM, Agent_constraints.MAX_ROLES) \
                      .filter(Agent_constraints.USER_ID == user_id).all()
    a_assignment_map = {agent_num: count for agent_num, count in a_assignments}
    La = [a_assignment_map.get(agent.AGENT_NUM, 0) for agent in agents]

    documents_cursor = doc_collection.find({"user_id": user_id})
    documents = await documents_cursor.to_list(length=None)

    evaluations = {}
    for doc in documents:
        agent_num = doc.get("agent_num")
        eval_data = doc.get("evaluation", {})
        evaluations[agent_num] = {
            role["ROLE_NAME"]: eval_data.get(role["DEFINING_WORD"], 0)
            for role in roles
        }

    # Step 7: Build score matrix
    matrix = [
        [evaluations.get(agent.AGENT_NUM, {}).get(role["ROLE_NAME"], 0) for role in roles]
        for agent in agents
    ]

    conflict_entries = db.query(Conflict_matrix).filter(Conflict_matrix.USER_ID == user_id).all()
    conflict_matrix = [[0] * len(agents) for _ in range(len(agents))]

    for c in conflict_entries:
        i = agent_index.get(c.AGENT_NUM_1)
        j = agent_index.get(c.AGENT_NUM_2)
        if i is not None and j is not None:
            conflict_matrix[i][j] = c.CONFLICT_VALUE
            conflict_matrix[j][i] = c.CONFLICT_VALUE 
    print(conflict_matrix)

    assignment_matrix = GMRACCF(matrix, L, La, conflict_matrix)  # If GMRA supports conflicts

    
    return {
        "matrix": assignment_matrix,
    }