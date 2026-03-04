from fastapi import FastAPI
from core.orchestrator import run_orchestrator

app = FastAPI(title="KI Konkret Demo - Agent API")

@app.get("/")
def read_root():
    return {"Event": "KI Konkret @ Campus Schwarzwald", "Status": "Running"}

@app.post("/process-request")
def process_request(query: str):
    # Hier wird der Orchestrator aufgerufen
    result = run_orchestrator(query)
    return result
