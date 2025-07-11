from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database.sql import get_db
from models.agent_model import Agent
from models.role_model import Role
from fastapi import APIRouter, HTTPException
import json
from database.mongo import get_roles_collection
import numpy as np
from numpy import dot
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer
from fastapi import Request
from database.mongo import get_documents_collection
from motor.motor_asyncio import AsyncIOMotorCollection
from entities.agent_entity import AgentResponse
from models.user_model import User
from typing import List
from services.mongo.evaluation_service import precompute_role_embeddings_with_faiss, get_embedding, analyze_documents
from services.data.DataPreprocessing import preprocess_text
import joblib

router = APIRouter()

@router.get("/evaluations/{user_id}")
async def get_evaluation_matrix(user_id: int,
                        db: Session = Depends(get_db), 
                        doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)):
    user = db.query(User).filter(User.USER_ID == user_id).first()
    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    roles = db.query(Role.ROLE_NAME, Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()

    documents_cursor = doc_collection.find({"user_id": user_id})
    documents = await documents_cursor.to_list(length=None)

    # 2. Build evaluation matrix from MongoDB
    evaluations = {}
    for doc in documents:
        agent_num = doc.get("agent_num")
        evaluation = doc.get("evaluation", {})
        evaluations[agent_num] = {
            role.ROLE_NAME: evaluation.get(role.DEFINING_WORD, 0)
            for role in roles
        }
    print(evaluations)
    return {
        "agents": agents,
        "roles": [role.ROLE_NAME for role in roles],
        "evaluations": evaluations,
        "user" :  {
            "COMPANY_NAME": user.COMPANY_NAME,
            "DEPARTMENT": user.COMPANY_DEPARTMENT
        }
    }


# Load model & embedding
embedder = SentenceTransformer("all-mpnet-base-v2")

 
model = joblib.load("trained_model.pkl")

# important inits
roles_info_cache = {}
text_to_role = []
faiss_index = None

async def initialize_roles(roles):

    global roles_info_cache, faiss_index, text_to_role
    roles_info = {}
    for role in roles:
        
        roles_info[role["name"]] = {
            "prompt": role["prompt"],
            "responsibilities": role["responsibilities"],
            "positive": role["positive"],
            "negative": role["negative"]
        }
    
    if not roles_info:
        raise HTTPException(status_code=404, detail="No roles found for this user")

    roles_info_cache = roles_info
    
    faiss_index, text_to_role = precompute_role_embeddings_with_faiss(roles_info_cache, embedder)

def keyword_overlap(agent_text, role_keywords):
    agent_words = set(agent_text.lower().split())  # or use NLP tokenizer
    overlap = len(agent_words & set(role_keywords))
    return overlap / max(len(role_keywords), 1)

@router.post("/evaluations/{user_id}")
async def evaluate_agents(
    user_id: int,
    agents: List[AgentResponse] = Body(...),
    db: Session = Depends(get_db),
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection),
    role_collection: AsyncIOMotorCollection = Depends(get_roles_collection)
):
    if not agents:
        raise HTTPException(status_code=404, detail="There are no agents in your system")

 
    '''
    with open('rolin.json', 'r', encoding='utf-8') as f:
        thingy = json.load(f)

        thingy = [
            {
                "name": role_name,
                "prompt": role_info.get("prompt", ""),
                "responsibilities": role_info.get("responsibilities", []),
                "positive": role_info.get("positive", []),
                "negative": role_info.get("negative", [])
            }
            for role_name, role_info in thingy.items()
        ]
        # Bulk insert all roles
        if thingy:
            result = await role_collection.insert_many(thingy)
            print(f"Inserted {len(result.inserted_ids)} roles.")
        else:
            print("No roles to insert.")
    '''


    # 1. Get role names from SQL DB
    roles = db.query(Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    role_names = [role[0] for role in roles]
    print(role_names)
    role_cursor = role_collection.find({
        "name": {"$in": role_names}
    })
    roles = await role_cursor.to_list(length=None)
    if not roles:
        raise HTTPException(status_code=404, detail="No roles found for this user")

    await initialize_roles(roles)

    # 2. Get all documents once
    documents_cursor = doc_collection.find({"user_id": user_id})
    all_documents = await documents_cursor.to_list(length=None)

    results = []

    for agent in agents:
        agent_id = agent.AGENT_NUM

        # Filter agent-specific documents
        agent_docs = [doc for doc in all_documents if doc.get("agent_num") == agent_id]
        
        # If no docs, use zero-vector strategy and assign 0.0 scores
        if not agent_docs:
            agent_result = {
                "agent_id": agent_id,
                "agent_name": agent.FIRST_NAME + ' ' + agent.LAST_NAME,
                "results": [{"role": role["name"], "predicted_score": 0.00} for role in roles]
            }
            
        else:
            # Embed agent documents
            agent_vec = analyze_documents(agent_docs, embedder)
            
            role_results = []
            for role in roles:
                role_name = role["name"]
                matched_role_name = role_name
                role_text = ""

                # Use cached role info if available - DO THIS OUTSIDE OF LOOP FOR EFFIENCENCY
                if role_name in roles_info_cache:
                    role_info = roles_info_cache[role_name]
                    prompt = role_info.get("prompt", "")
                    responsibilities =" ".join(role_info.get("responsibilities", []))
                    positive = " ".join(role_info.get("positive", []))
                    negative = " ".join(role_info.get("negative", []))
                    # The requirements and responsibilties of this role are {responsibilities}. 
                    role_text = f"{prompt}. The requirements and responsibilties of this role are {responsibilities}. This role involves: {positive}. Avoid: {negative}."
                    role_vec = get_embedding(role_text, embedder)
                    role_vec = np.concatenate([role_vec, np.zeros(4)])  # sentiment placeholder to match shape

                if not role_text:
                    role_text = role_name


                combined_vec = np.concatenate([
                    agent_vec,
                    role_vec,
                    np.abs(agent_vec - role_vec),
                    agent_vec * role_vec,
                ]).reshape(1, -1)

                pred_score = float(model.predict(combined_vec)[0])
                print(f"Agent {agent_id}, Role {matched_role_name}, Predicted Score: {pred_score}")

                role_results.append({
                    "role": matched_role_name,
                    "predicted_score": pred_score
                })

            agent_result = {
                "agent_id": agent_id,
                "agent_name": agent.FIRST_NAME + ' ' + agent.LAST_NAME,
                "results": role_results
            }
            
            # update in mongo
            evaluation_update = {
                f"evaluation.{r['role']}": r["predicted_score"]
                for r in agent_result["results"]
            }

            await doc_collection.update_many(
                {
                    "user_id": user_id,
                    "agent_num": agent_id
                },
                {
                    "$set": evaluation_update
                }
            )


        results.append(agent_result)

    return {"evaluations": results}



@router.put("/evaluations/{user_id}")
async def update_agent_evaluations(
    user_id: int,
    request: Request,
    doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection),
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        evaluations = data.get("evaluations", {})

        if not isinstance(evaluations, dict):
            raise HTTPException(status_code=400, detail="Invalid evaluations format.")

        roles = db.query(Role).filter(Role.USER_ID == user_id).all()
        role_map = {role.ROLE_NAME: role.DEFINING_WORD for role in roles}

        for agent_num_str, role_scores in evaluations.items():
            if not isinstance(role_scores, dict):
                continue

            try:
                agent_num = int(agent_num_str)
            except ValueError:
                continue

            # Step 2: Build new evaluation using defining words
            evaluation_update = {
                f"evaluation.{role_map.get(role, role)}": score
                for role, score in role_scores.items()
                if isinstance(score, (int, float))
            }

            if evaluation_update:
                result = await doc_collection.update_one(
                {
                    "user_id": user_id,
                    "agent_num": agent_num
                },
                    {"$set":  evaluation_update}
                )
                print(f"Agent {agent_num}: matched={result.matched_count}, modified={result.modified_count}")
                print(f"Updated with: {evaluation_update}")
        docs = await doc_collection.find({"user_id": str(user_id), "agent_num": str(agent_num)}).to_list(length=10)
        print(docs)
        return {"message": "Evaluations updated successfully"}

    except Exception as e:
        print("Error during evaluation update:", e)
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")