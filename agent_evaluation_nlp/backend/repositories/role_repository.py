from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.sql import get_db
from models.role_model import Role
from entities.role_entity import RoleResponse, RoleCreate, KeywordCreate
from typing import List
from collections import defaultdict
from motor.motor_asyncio import AsyncIOMotorCollection
from database.mongo import get_roles_collection
from database.mongo import get_documents_collection
from services.mongo.role_service import get_embedding, precompute_role_embeddings_with_faiss, add_keyword_mongo
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
router = APIRouter()

@router.get("/roles/{user_id}", response_model=List[RoleResponse])
def get_roles(user_id: int, db: Session = Depends(get_db)):
    roles = db.query(Role).filter(Role.USER_ID == user_id).all()

    response = [
        RoleResponse(
            ROLE_NAME=role.ROLE_NAME,
            ROLE_KEYWORD=role.ROLE_KEYWORD,
            DEFINING_WORD=role.DEFINING_WORD
        )
        for role in roles
    ]
    return response

@router.post("/roles/{user_id}")
async def create_role(user_id: int, role: RoleCreate, 
                      db: Session = Depends(get_db),
                      role_collection: AsyncIOMotorCollection = Depends(get_roles_collection),
                      doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)):
    print(f"Received POST for user {user_id} with role data: {role}")
    matched_role_name = None
    trait_name = role.ROLE_NAME
    role_cursor = role_collection.find({})
    roles_docs = await role_cursor.to_list(length=None)
    roles_info = {
        doc.get("name", "default_name"): {"positive": doc.get("positive", [])}
        for doc in roles_docs
    }
    roles = db.query(Role).filter(Role.USER_ID == user_id).all()
    existing_role_names = {r.ROLE_NAME for r in roles}

    embedder = SentenceTransformer("all-mpnet-base-v2")
    role_names = list(roles_info.keys())
    print("Fetched role names from Mongo:", role_names)
    role_name_embeddings = embedder.encode(role_names, convert_to_numpy=True).astype(np.float32)

    role_name_faiss = faiss.IndexFlatL2(role_name_embeddings.shape[1])
    role_name_faiss.add(role_name_embeddings)


    
    faiss_index, text_to_role = precompute_role_embeddings_with_faiss(roles_info, embedder)

    
    MAX_L2_DISTANCE = 0.8
    trait_vec = get_embedding(trait_name, embedder).astype(np.float32).reshape(1, -1)
    D, I = role_name_faiss.search(trait_vec, 1)
    top_idx = I[0][0]
    distance = D[0][0]

    matched_role_name = None
    if top_idx != -1 and distance < MAX_L2_DISTANCE:
        matched_name = role_names[top_idx]
        if matched_name in roles_info:
            matched_role_name = matched_name
    if matched_role_name == None:
        trait_vec = get_embedding(trait_name, embedder).astype(np.float32).reshape(1, -1)
        D, I = faiss_index.search(trait_vec, 1)
        top_idx = I[0][0]
        distance = D[0][0]

        if top_idx != -1 and distance < MAX_L2_DISTANCE:
            _, matched_role = text_to_role[top_idx]
            if matched_role in roles_info:
                if matched_role_name not in existing_role_names:
                    matched_role_name = matched_role

    if matched_role_name is None:
        matched_role_name = role.ROLE_NAME
        new_role_doc = {
            "name": role.ROLE_NAME,
            "prompt": "",
            "responsibilities": "",
            "positive": role.ROLE_KEYWORDS,
            "negative": []
        }
        print("Created roles:", new_role_doc)
        await role_collection.insert_one(new_role_doc)
    print("MADE IT HERE")
    # Bulk update documents missing this role evaluation
    await doc_collection.update_many(
        {
            "user_id": user_id,
            f"evaluation.{matched_role_name}": {"$exists": False}
        },
        {
            "$set": {f"evaluation.{matched_role_name}": 0}
        }
    )
    created_roles = []
    if not role.ROLE_KEYWORDS: # if no keyroles were defined
        db_role = Role(
            ROLE_NAME=role.ROLE_NAME,
            ROLE_KEYWORD="Unspecified",
            USER_ID=user_id,
            DEFINING_WORD=matched_role_name
        )
        db.add(db_role)
        try:
            db.commit()
            db.refresh(db_role)  # Now it's safe to refresh
        except Exception as e:
            db.rollback()
            raise e
        created_roles.append(RoleResponse(
            ROLE_NAME=role.ROLE_NAME,
            ROLE_KEYWORD="Unspecified",
        ))
    else:
        for keyword in role.ROLE_KEYWORDS:
            db_role = Role(
                ROLE_NAME=role.ROLE_NAME,
                ROLE_KEYWORD=keyword,
                USER_ID=user_id,
                DEFINING_WORD=matched_role_name
            )
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            created_roles.append(RoleResponse(
                ROLE_NAME=role.ROLE_NAME,
                ROLE_KEYWORD=keyword,
            ))

    return created_roles


@router.post("/keyword/{user_id}", response_model=RoleResponse)
async def add_keyword_to_role(
    user_id: int,
    keyword_data: KeywordCreate,
    db: Session = Depends(get_db),
    role_collection: AsyncIOMotorCollection = Depends(get_roles_collection)
):
    # Get existing defining word for that role (if any)
    existing_role = db.query(Role).filter(
        Role.USER_ID == user_id,
        Role.ROLE_NAME == keyword_data.ROLE_NAME
    ).distinct().first()

    if existing_role.ROLE_KEYWORD == "Unspecified":
        db.delete(existing_role)
    
    # Save to SQL database
    db_role = Role(
        ROLE_NAME=keyword_data.ROLE_NAME,
        ROLE_KEYWORD=keyword_data.ROLE_KEYWORD,
        USER_ID=user_id,
        DEFINING_WORD=existing_role.DEFINING_WORD
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    res = await add_keyword_mongo(keyword_data.ROLE_KEYWORD, existing_role.DEFINING_WORD, role_collection)
    print(res)

    return RoleResponse(
        ROLE_NAME=db_role.ROLE_NAME,
        ROLE_KEYWORD=db_role.ROLE_KEYWORD
    )

@router.delete("/roles/{role_name}")
async def delete_role(role_name: str,
                      userId: int,  # ← this picks up ?userId= from query string
                      db: Session = Depends(get_db),
                      doc_collection: AsyncIOMotorCollection = Depends(get_documents_collection)):
    # delete from sql
    roles_to_delete = db.query(Role).filter(Role.ROLE_NAME == role_name).all()
    if not roles_to_delete:
        raise HTTPException(status_code=404, detail="Role not found")
    for role in roles_to_delete:
        db.delete(role)
    db.commit()

    # delete from mongo
    defining_word = roles_to_delete[0].DEFINING_WORD
    await doc_collection.update_many(
        {"user_id": userId},
        {"$unset": {f"evaluation.{defining_word}": ""}}
    )
    return {"message": f"Role '{role_name}' and all its keywords deleted"}