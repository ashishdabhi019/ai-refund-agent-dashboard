from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory session storage
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.post("/chat")
async def chat(request: ChatRequest):
    # Get or create conversation history
    if request.session_id not in sessions:
        sessions[request.session_id] = []
    
    history = sessions[request.session_id]
    result = run_agent(request.message, history)
    
    # Update history (without the last user message since run_agent handles it)
    sessions[request.session_id] = result["messages"]
    
    return {
        "response": result["response"],
        "logs": result["logs"]
    }

from crm_data import CRM_DATABASE, reset_crm_database

@app.get("/orders")
async def get_orders():
    return CRM_DATABASE

@app.post("/reset")
async def reset(request: dict):
    session_id = request.get("session_id", "default")
    sessions[session_id] = []
    reset_crm_database()
    return {"status": "reset"}

@app.get("/health")
async def health():
    return {"status": "ok"}