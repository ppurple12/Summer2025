from fastapi import APIRouter, UploadFile, File, Depends, Query
import os
import tempfile
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorCollection

from services.data.LoadingPipeline import load_all_files
from services.data.DataPreprocessing import format_data
from database.sql import get_db
from database.mongo import get_documents_collection
from models.agent_model import Agent
from models.role_model import Role

router = APIRouter()

# handles uploading documents 
# adds new instance if agent document never been seen
# adds document to known documents if instance exists
@router.post("/upload-folder/{user_id}")
async def upload_folder(
    user_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db), # sql db
    mongo_collection: AsyncIOMotorCollection = Depends(get_documents_collection) # mongo db
):
    # creates a virtual directory from the documents given
    with tempfile.TemporaryDirectory() as tmpdir:
        for file in files:
            file_path = os.path.join(tmpdir, file.filename)
            content = await file.read()
            print(f"Saving file: {file.filename}, size: {len(content)} bytes")
            with open(file_path, "wb") as f:
                f.write(content)
        
        raw_data = load_all_files(tmpdir)
        

    # loads agents n roles
    roles = db.query(Role.DEFINING_WORD).filter(Role.USER_ID == user_id).distinct().all()
    agents = db.query(Agent).filter(Agent.USER_ID == user_id).all()
    agent_names = [f"{agent.FIRST_NAME} {agent.LAST_NAME}" for agent in agents]
    agent_ids = [agent.AGENT_ID for agent in agents]
    print(agent_names)
    # creates instances of agents
    formatted = format_data(raw_data, agent_names, agent_ids)
    print(formatted)
    inserted_count = 0
    skipped_entries = []

    # checks each document that has been uploaded
    for doc in formatted:
        agent_id = doc["agent_id"]
        agent_name = doc["agent_name"]
        new_docs = doc["documents"]

        # Check if the agent already has a MongoDB entry
        existing_doc = await mongo_collection.find_one({"agent_id": agent_id})

        if not existing_doc:
            # Insert the entire document if it's a new agent
            agent_abilities = {}
            agent_num = None
            for agent in agents:
                if agent.AGENT_ID == agent_id and (agent.FIRST_NAME + " " + agent.LAST_NAME).lower() == agent_name:
                    agent_num = agent.AGENT_NUM
                    break

            for role in roles:
                agent_abilities[role.DEFINING_WORD] = 0  
            await mongo_collection.insert_one({
                "user_id": user_id,
                "agent_id": agent_id,
                "agent_num": agent_num,
                "agent_name": agent_name,
                "documents": new_docs,
                "evaluation": agent_abilities
            })
            inserted_count += sum(len(v) for v in new_docs.values())
            continue

        # Agent exists — need to update only new documents
        updates = {}
        for category, entries in new_docs.items():
            existing_hashes = {
                entry["_hash"]
                for entry in existing_doc.get("documents", {}).get(category, [])
                if "_hash" in entry
            }

            new_unique = []
            for entry in entries:
                entry_hash = entry.get("_hash")
                if not entry_hash:
                    continue
                if entry_hash in existing_hashes:
                    skipped_entries.append({
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "category": category,
                        "hash": entry_hash,
                        "reason": "Duplicate entry"
                    })
                else:
                    new_unique.append(entry)

            if new_unique:
                # Append to the update set
                updates.setdefault(f"documents.{category}", []).extend(new_unique)

        # Apply updates if there are any
        if updates:
            update_query = {
                "$push": {
                    field: {"$each": docs}
                    for field, docs in updates.items()
                }
            }
            await mongo_collection.update_one(
                {"agent_id": agent_id},
                update_query
            )
            inserted_count += sum(len(docs) for docs in updates.values())

    return {
        "inserted_count": inserted_count,
        "skipped_duplicates": skipped_entries
    }