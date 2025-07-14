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

