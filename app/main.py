
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import time

app = FastAPI(
    title="DeploySimple Demo Backend",
    version="0.1.0",
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

    This lets you test the whole UX flow while AWS stack is being created.
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
