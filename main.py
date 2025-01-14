from fastapi import FastAPI, Request, Response, Cookie, HTTPException
from pydantic import BaseModel
from typing import Optional
from inference_pipeline import inference_methods
import redis
import json
import uuid

inf = inference_methods.dndCharacter()

app = FastAPI()

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

SESSION_TIMEOUT = 3600  # 1 hour in seconds

@app.middleware("http")
async def delete_redis_on_swagger_refresh(request: Request, call_next):
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        redis_client.flushdb()  
    response = await call_next(request)
    return response


# @app.get("/start_session")
# def start_session(response: Response):
#     session_id = str(uuid.uuid4())
#     response.set_cookie(key="session_id", value=session_id, max_age=SESSION_TIMEOUT)
#     return {"message": "session started", "session_id": session_id}

@app.post('/store-output/{endpoint_name}')
def store_output(endpoint_name: str, data: dict, session_id: str = Cookie(None)):
    print(session_id)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID missing")
    redis_key = f"{session_id}:{endpoint_name}"
    redis_client.setex(redis_key, SESSION_TIMEOUT, json.dumps(data))
    return {"message": f"Data stored for endpoint '{endpoint_name}'"}

@app.get("/get-output/{endpoint_name}/")
def get_output(endpoint_name: str, session_id: str = Cookie(None)):
    print(session_id)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID missing")
    redis_key = f"{session_id}:{endpoint_name}"
    data = redis_client.get(redis_key)
    if data:
        return {"endpoint": endpoint_name, "data": json.loads(data)}
    
@app.get("/race")
def get_race():
    if not get_output("get_race"):
        race_name = inf.get_race()
        store_output("get_race", race_name)
    output_race = get_output("get_race")
    return output_race

@app.get("/class")
def get_class():
    if not get_output("get_class"):
        class_name = inf.get_class()
        store_output("get_class", class_name)
    output_class = get_output("get_class")
    return output_class

@app.get("/background")
def get_background():
    if not get_output("get_background"):
        background_name = inf.get_background()
        store_output("get_background", background_name)
    output_background = get_output("get_background")
    return output_background

@app.get("/class_context")
def get_class_context(class_name: str):
    if not get_output("get_class_context"):
        class_context = inf.get_class_context(class_name)
        store_output("get_class_context", class_context)
    output_class_context = get_output("get_class_context")
    return output_class_context

@app.get("/race_context")
def get_race_context(race_name: str):
    if not get_output("get_race_context"):
        race_context = inf.get_race_context(race_name)
        store_output("get_race_context", race_context)
    output_race_context = get_output("get_race_context")
    return output_race_context

@app.get("/background_context")
def get_background_context(background_name: str):
    if not get_output("get_background_context"):
        background_context = inf.get_background_context(background_name)
        store_output("get_background_context", background_context)
    output_background_context = get_output("get_background_context")
    return output_background_context

@app.get("/abilities")
def get_abilities(class_name: str, class_context: str):
    if not get_output("get_abilities"):
        class_abilities = inf.get_abilities(class_name, class_context)
        store_output("get_abilities", class_abilities)
    output_abilities = get_output("get_abilities")
    return output_abilities


@app.get("/ability_scores")
def get_ability_scores():
    if not get_output("get_abilities"):
        raise HTTPException(status_code=400, detail="Abilities not assigned")
    output_abilities = get_output("get_abilities")
    if not get_output("get_ability_scores"):
        ability_scores = inf.assign_scores(output_abilities['data'])
        store_output("get_ability_scores", ability_scores)
    output_abilities = get_output("get_ability_scores")
    return output_abilities

@app.get("/assign_ability_modifier")
def get_ability_modifier(strength_score: int, dexterity_score: int, constitution_score: int, intelligence_score: int, wisdom_score: int, charisma_score: int):
    return {"assigned_modifiers": inf.ability_modifier(strength_score, dexterity_score, constitution_score, intelligence_score, wisdom_score, charisma_score)}

@app.get("/proficieny_modifier")
def get_proficiency_modifier():
    return {"proficiency_modifier": inf.proficiency_modifier()}

@app.get("/saving_throws")
def get_saving_throws(class_name: str, class_context: str):
    return {"saving_throws": inf.saving_throws(class_name, class_context)}
