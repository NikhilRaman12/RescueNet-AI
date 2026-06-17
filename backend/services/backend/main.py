from fastapi import FastAPI
from backend.services.rescue_graph import run_rescue_graph

app = FastAPI(title="RescueNet AI API")


@app.get("/")
def root():
    return {"status": "RescueNet AI running"}


@app.post("/run")
def run_mission(payload: dict):
    location = payload.get("location", "Hyderabad")
    disaster_type = payload.get("disaster_type", "flood")
    query = payload.get("query", "")

    result = run_rescue_graph({
        "location": location,
        "disaster_type": disaster_type,
        "query": query
    })

    return result
