from fastapi import FastAPI
from repositories.user_repository import router as user_router
from repositories.agent_repository import router as agent_router
from repositories.role_repository import router as role_router
from repositories.document_repository import router as document_repository
from repositories.evaluation_repository import router as evaluation_repository
from repositories.assignment_repository import router as assignment_repository
from fastapi.middleware.cors import CORSMiddleware
from database.sql import get_db
from fastapi.staticfiles import StaticFiles
import os
import requests
import onnxruntime

app = FastAPI()
from database.sql import Base, engine
Base.metadata.create_all(bind=engine)
import nltk
print("👋 app.py top-level code running")
nltk.download("vader_lexicon")


print("Working directory:", os.getcwd())
print("agent_evaluation_nlp contents:", os.listdir("backend"))
print("services contents:", os.listdir("backend/services"))
MODEL_PATH = "backend/all_mpnet_base_v2.onnx"
MODEL_URL = "https://huggingface.co/pppurple12/embedding_model/resolve/main/all_mpnet_base_v2.onnx"

def ensure_model_downloaded():
    if not os.path.exists(MODEL_PATH) or os.path.getsize(MODEL_PATH) < 10_000_000:
        print("Downloading ONNX model from Hugging Face...")
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        r = requests.get(MODEL_URL, stream=True)
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Model downloaded! Size: {os.path.getsize(MODEL_PATH)} bytes (expected ~{total})")
    else:
        print("Model already exists and looks complete.")

@app.on_event("startup")
async def startup_event():
    from agent_evaluation_nlp.backend.services.onnx_services import get_ort_session, get_mlp_session
    print("✔ Verifying ONNX model presence...")
    ensure_model_downloaded()
    # Just warm up once if you want
    get_ort_session()
    get_mlp_session()

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

