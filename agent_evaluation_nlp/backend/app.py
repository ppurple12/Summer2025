from fastapi import FastAPI
from repositories.user_repository import router as user_router
from repositories.agent_repository import router as agent_router
from repositories.role_repository import router as role_router
from repositories.document_repository import router as document_repository
from repositories.evaluation_repository import router as evaluation_repository
from repositories.assignment_repository import router as assignment_repository
from fastapi.middleware.cors import CORSMiddleware
from database.sql import get_db
from database.mongo import client
from fastapi.staticfiles import StaticFiles
import os
import requests
import onnxruntime
import numpy as np
import faiss
from services.mongo.role_service import get_embedding, precompute_role_embeddings_with_faiss

role_name_faiss = None
faiss_index = None
text_to_role = None
roles_info_cache = None

async def initialize_faiss_and_embeddings(role_collection):
    global role_name_faiss, faiss_index, text_to_role, roles_info_cache

    roles_docs = await role_collection.find({}).to_list(length=None)
    roles_info_cache = {
        doc.get("name", ""): {"positive": doc.get("positive", [])}
        for doc in roles_docs
    }

    role_names = list(roles_info_cache.keys())

    role_name_embeddings = np.array([get_embedding(name) for name in role_names], dtype=np.float32)
    role_name_faiss = faiss.IndexFlatL2(role_name_embeddings.shape[1])
    role_name_faiss.add(role_name_embeddings)

    faiss_index, text_to_role = precompute_role_embeddings_with_faiss(roles_info_cache)

    globals()['faiss_index'] = faiss_index
    globals()['text_to_role'] = text_to_role

app = FastAPI()
from database.sql import Base, engine
Base.metadata.create_all(bind=engine)
import nltk
print("👋 app.py top-level code running")
nltk.download("vader_lexicon")


print("Working directory:", os.getcwd())
print("Root contents:", os.listdir("."))
MODEL_PATH = "all_mpnet_base_v2.onnx"
MODEL_URL = "https://huggingface.co/pppurple12/embedding_model/resolve/main/all_mpnet_base_v2.onnx"


@app.on_event("startup")
async def verify_mongo_connection():
    try:
        await client.admin.command("ping")
        print("✅ MongoDB connection established")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",  "http://localhost:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router,  prefix="/api") 
app.include_router(agent_router, prefix="/api")
app.include_router(role_router, prefix="/api") 
app.include_router(document_repository, prefix="/api")
app.include_router(evaluation_repository, prefix="/api")
app.include_router(assignment_repository, prefix="/api/assignments")

# Mount the frontend build folder as static files
frontend_path = os.path.join(os.path.dirname(__file__), "frontend_dist")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
print("Working directory:", os.getcwd())

@app.get("/")
def root():
    return {"message": "Welcome to Auto Agent Evaluation API"}

