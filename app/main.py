from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import time

app = FastAPI(
    title="DeploySimple Demo Backend",
    version="0.1.0",
)

# 👇 CORS CONFIG – IMPORTANT
# Add your frontend origins here
origins = [
    "http://localhost:5173",              # Vite dev server
    "http://localhost:3000",              # if you ever use CRA/Next
    "https://deploy-simple-frontend.com", # your real domain later
    "https://deploy-simple-backend.onrender.com",  # optional, for testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # for demo, allow all; in prod, use `origins`
    allow_credentials=True,
    allow_methods=["*"],          # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

# In-memory store just for demo (will reset on restart)
connections: Dict[str, Dict[str, Any]] = {}


class CheckConnectionRequest(BaseModel):
    externalId: str
    customerId: str


@app.get("/")
def root():
    return {"status": "ok", "service": "deploysimple-demo-backend"}


@app.post("/api/aws/check-connection")
def check_connection(body: CheckConnectionRequest):
    """
    Demo logic:
    - First time we see (customerId, externalId): mark as 'started', return connected: false
    - After ~20 seconds of polling: return connected: true with dummy connection details
    """
    key = f"{body.customerId}:{body.externalId}"
    now = time.time()

    entry = connections.get(key)

    if entry is None:
        # First time we see this pair
        connections[key] = {"first_seen": now}
        return {"connected": False}

    elapsed = now - entry["first_seen"]

    # After 20 seconds, pretend connection is ready
    if elapsed >= 20:
        if "connection" not in entry:
            entry["connection"] = {
                "awsAccountId": "000000000000",  # dummy for now
                "region": "us-east-1",
                "roleArn": "arn:aws:iam::000000000000:role/DeploySimple-Demo",
            }
        return {"connected": True, "connection": entry["connection"]}

    # Still 'connecting'
    return {"connected": False}
