from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent, is_openrouter
from refund_policy import REFUND_POLICY
import json

app = FastAPI(title="AI Refund Agent API", version="2.0")

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
    """Process a customer refund request through the AI agent."""
    # Get or create conversation history
    if request.session_id not in sessions:
        sessions[request.session_id] = []
    
    history = sessions[request.session_id]
    result = run_agent(request.message, history)
    
    # Update history
    sessions[request.session_id] = result["messages"]
    
    return {
        "response": result["response"],
        "logs": result["logs"]
    }

from crm_data import CRM_DATABASE, reset_crm_database

@app.get("/orders")
async def get_orders():
    """Get all CRM orders for the admin dashboard."""
    return CRM_DATABASE

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get a specific order by ID."""
    order = CRM_DATABASE.get(order_id.upper())
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order

@app.get("/policy")
async def get_policy():
    """Get the full refund policy document."""
    return {"policy": REFUND_POLICY}

@app.get("/status")
async def get_status():
    """Get agent mode and API status."""
    return {
        "status": "ok",
        "mode": "live" if is_openrouter else "simulation",
        "model": "meta-llama/llama-3.3-70b-instruct" if is_openrouter else "simulation",
        "total_orders": len(CRM_DATABASE),
        "active_sessions": len(sessions)
    }

@app.post("/reset")
async def reset(request: dict):
    """Reset conversation session and CRM database state."""
    session_id = request.get("session_id", "default")
    sessions[session_id] = []
    reset_crm_database()
    return {"status": "reset", "session_id": session_id}

@app.get("/health")
async def health():
    return {"status": "ok"}