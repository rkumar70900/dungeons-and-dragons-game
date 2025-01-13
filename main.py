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
    # Check if the request is for the Swagger UI
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        redis_client.flushdb()  # Clear the Redis database
        print("Redis database cleared.")
    
    # Proceed to the next request handler
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

    # Key for this endpoint's output
    redis_key = f"{session_id}:{endpoint_name}"
    # Store data in Redis with expiration
    redis_client.setex(redis_key, SESSION_TIMEOUT, json.dumps(data))
    return {"message": f"Data stored for endpoint '{endpoint_name}'"}

@app.get("/get-output/{endpoint_name}/")
def get_output(endpoint_name: str, session_id: str = Cookie(None)):
    print(session_id)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID missing")

    # Key for this endpoint's output
    redis_key = f"{session_id}:{endpoint_name}"
    data = redis_client.get(redis_key)
    if data:
        return {"endpoint": endpoint_name, "data": json.loads(data)}
    # raise HTTPException(status_code=404, detail=f"No data found for endpoint '{endpoint_name}'")

    
@app.get("/race")
def get_race():
    if not get_output("get_race"):
        print("New Session")
        race_name = inf.get_race()
        store_output("get_race", race_name)
    else:
        print("Old Session")
    output_race = get_output("get_race")
    return output_race

@app.get("/class")
def get_class():
    if not get_output("get_class"):
        print("New Session")
        class_name = inf.get_class()
        store_output("get_class", class_name)
    else:
        print("Old Session")
    output_class = get_output("get_class")
    return output_class

@app.get("/background")
def get_background():
    return {"background": inf.get_background()}

@app.get("/class_context")
def get_class_context(class_name: str):
    return {"class_context": inf.get_class_context(class_name)}

@app.get("/race_context")
def get_race_context(race_name: str):
    return {"race_context": inf.get_race_context(race_name)}

@app.get("/background_context")
def get_race_context(background_name: str):
    return {"background_context": inf.get_background_context(background_name)}

@app.get("/ability_scores")
def get_ability_scores(class_name: str, class_context: str):
    return {"ability_scores": inf.assign_scores(class_name, class_context)}

@app.get("/assign_ability_modifier")
def get_ability_modifier(strength_score: int, dexterity_score: int, constitution_score: int, intelligence_score: int, wisdom_score: int, charisma_score: int):
    return {"assigned_modifiers": inf.ability_modifier(strength_score, dexterity_score, constitution_score, intelligence_score, wisdom_score, charisma_score)}

@app.get("/proficieny_modifier")
def get_proficiency_modifier():
    return {"proficiency_modifier": inf.proficiency_modifier()}

@app.get("/saving_throws")
def get_saving_throws(class_name: str, class_context: str):
    return {"saving_throws": inf.saving_throws(class_name, class_context)}
