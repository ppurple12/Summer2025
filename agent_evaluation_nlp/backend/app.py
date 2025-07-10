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

app = FastAPI()
from database.sql import Base, engine
Base.metadata.create_all(bind=engine)
import nltk
nltk.download("vader_lexicon")
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


@app.get("/")
def root():
    return {"message": "Welcome to Auto Agent Evaluation API"}

