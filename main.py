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

@app.post('/store-output/{endpoint_name}')
def store_output(endpoint_name: str, data: dict, session_id: str = Cookie(None)):
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
def get_class_context():
    if not get_output("get_class"):
        raise HTTPException(status_code=400, detail="Class not assigned")
    class_name = get_output("get_class")['data']
    if not get_output("get_class_context"):
        class_context = inf.get_class_context(class_name)
        store_output("get_class_context", class_context)
    output_class_context = get_output("get_class_context")
    return output_class_context

@app.get("/race_context")
def get_race_context():
    if not get_output("get_race"):
        raise HTTPException(status_code=400, detail="Race not assigned")
    race_name = get_output("get_race")['data']
    if not get_output("get_race_context"):
        race_context = inf.get_race_context(race_name)
        store_output("get_race_context", race_context)
    output_race_context = get_output("get_race_context")
    return output_race_context

@app.get("/background_context")
def get_background_context():
    if not get_output("get_background"):
        raise HTTPException(status_code=400, detail="Background not assigned")
    background_name = get_output("get_background")['data']
    if not get_output("get_background_context"):
        background_context = inf.get_background_context(background_name)
        store_output("get_background_context", background_context)
    output_background_context = get_output("get_background_context")
    return output_background_context

@app.get("/abilities")
def get_abilities():
    if not get_output("get_class") and get_output("get_class_context"):
        raise HTTPException(status_code=400, detail="Class and Class Context not assigned")
    class_name = get_output("get_class")['data']
    class_context = get_output("get_class_context")['data']
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
def get_ability_modifier():
    if not get_output("get_ability_scores"):
        raise HTTPException(status_code=400, detail="Ability scores not assigned")
    output_ability_scores = get_output("get_ability_scores")['data']
    if not get_output("get_ability_modifier"):
        ability_modifier = inf.ability_modifier(output_ability_scores)
        store_output("get_ability_modifier", ability_modifier)
    output_ability_modifier = get_output("get_ability_modifier")
    return output_ability_modifier

@app.get("/proficieny_modifier")
def get_proficiency_modifier():
    if not get_output("get_proficiency_modifier"):
        proficiency_modifier = inf.proficiency_modifier()
        store_output("get_proficiency_modifier", proficiency_modifier)
    output_proficiency_modifier = get_output("get_proficiency_modifier")
    return output_proficiency_modifier

@app.get("/saving_throws")
def get_saving_throws():
    if not get_output("get_class") and get_output("get_class_context"):
        raise HTTPException(status_code=400, detail="Class and Class Context not assigned")
    class_name = get_output("get_class")['data']
    class_context = get_output("get_class_context")['data']
    if not get_output("get_ability_scores"):
        raise HTTPException(status_code=400, detail="Ability scores not assigned")
    ability_scores = get_output("get_ability_scores")['data']
    if not get_output("get_proficiency_modifier"):
        raise HTTPException(status_code=400, detail="Proficiency modifier not assigned")
    proficiency_modifier = get_output("get_proficiency_modifier")['data']['proficiency_modifier']
    if not get_output("get_saving_throws"):
        saving_throws = inf.saving_throws(class_name, class_context, ability_scores, proficiency_modifier)
        store_output("get_saving_throws", saving_throws)
    output_saving_throws = get_output("get_saving_throws")
    return output_saving_throws

@app.get("/skills")
def get_skills():
    if not get_output("get_class") and get_output("get_class_context"):
        raise HTTPException(status_code=400, detail="Class and Class Context not assigned")
    class_name = get_output("get_class")['data']
    class_context = get_output("get_class_context")['data']
    if not get_output("get_background") and get_output("get_background_context"):   
        raise HTTPException(status_code=400, detail="Background and Background Context not assigned")
    background_name = get_output("get_background")['data']
    background_context = get_output("get_background_context")['data']
    if not get_output("get_ability_scores"):
        raise HTTPException(status_code=400, detail="Ability scores not assigned")
    ability_scores = get_output("get_ability_scores")['data']
    if not get_output("get_proficiency_modifier"):
        raise HTTPException(status_code=400, detail="Proficiency modifier not assigned")
    proficiency_modifier = get_output("get_proficiency_modifier")['data']['proficiency_modifier']
    if not get_output("get_skills"):
        skills = inf.get_skills(class_name, background_name, class_context, background_context, ability_scores, proficiency_modifier)
        store_output("get_skills", skills)
    output_skills = get_output("get_skills")
    return output_skills

@app.get("/passive_perception")
def get_passive_perception():
    if not get_output("get_skills"):
        raise HTTPException(status_code=400, detail="Skills not assigned")
    perception = get_output("get_skills")['data']['Perception']
    if not get_output("get_passive_perception"):
        passive_perception = inf.get_passive_perception(perception)
        store_output("get_passive_perception", passive_perception)
    output_passive_perception = get_output("get_passive_perception")
    return output_passive_perception

@app.get("/proficiencies_languages")
def get_proficiencies_languages():
    if not get_output("get_class") and get_output("get_class_context"):
        raise HTTPException(status_code=400, detail="Class and Class Context not assigned")
    if not get_output("get_background") and get_output("get_background_context"):   
        raise HTTPException(status_code=400, detail="Background and Background Context not assigned")
    class_name = get_output("get_class")['data']
    class_context = get_output("get_class_context")['data']
    background_name = get_output("get_background")['data']
    background_context = get_output("get_background_context")['data']
    if not get_output("get_proficiencies_languages"):
        proficiencies_languages = inf.get_proficiencies_languages(class_name, background_name, class_context, background_context)
        store_output("get_proficiencies_languages", proficiencies_languages)
    output_proficiencies_languages = get_output("get_proficiencies_languages")
    return output_proficiencies_languages

@app.get("/equipment_money")
def get_equipment_money():
    if not get_output("get_class") and get_output("get_class_context"):
        raise HTTPException(status_code=400, detail="Class and Class Context not assigned")
    if not get_output("get_background") and get_output("get_background_context"):   
        raise HTTPException(status_code=400, detail="Background and Background Context not assigned")
    class_name = get_output("get_class")['data']
    class_context = get_output("get_class_context")['data']
    background_name = get_output("get_background")['data']
    background_context = get_output("get_background_context")['data']
    if not get_output("get_equipment_money"):
        equipment_money = inf.get_equipment_money(class_name, background_name, class_context, background_context)
        store_output("get_equipment_money", equipment_money)
    output_equipment_money = get_output("get_equipment_money")
    return output_equipment_money

@app.get("/attacks")
def get_attacks():
    if not get_output("get_proficiencies_languages"):
        raise HTTPException(status_code=400, detail="Proficiencies and Languages not assigned")
    weapons = get_output("get_proficiencies_languages")['data']['weapons']
    if not get_output("get_ability_modifier"):
        raise HTTPException(status_code=400, detail="Ability mofidiers not assigned")
    ability_modifier = get_output("get_ability_modifier")['data']
    if not get_output("get_proficiency_modifier"):
        raise HTTPException(status_code=400, detail="Proficiency modifier not assigned")
    proficiency_modifier = get_output("get_proficiency_modifier")['data']['proficiency_modifier']
    if not get_output("get_attacks"):
        attacks = inf.get_attacks_damage(weapons, ability_modifier["dexterity"], ability_modifier["strength"], proficiency_modifier)
        store_output("get_attacks", attacks)
    output_attacks = get_output("get_attacks")
    return output_attacks

@app.get("/armor")
def get_armor_class():
    if not get_output("get_proficiencies_languages"):
        raise HTTPException(status_code=400, detail="Proficiencies and Languages not assigned")
    armor = get_output("get_proficiencies_languages")['data']['armor']
    if not get_output("get_ability_modifier"):
        raise HTTPException(status_code=400, detail="Ability mofidiers not assigned")
    dexterity_modifier = get_output("get_ability_modifier")['data']['dexterity']
    if not get_output("get_armor"):
        armor = inf.get_armor_class(armor, dexterity_modifier)
        store_output("get_armor_class", armor)
    output_armor_class = get_output("get_armor_class") 
    return output_armor_class

@app.get("/initative")
def get_initiative():
    if not get_output("get_ability_modifier"):
        raise HTTPException(status_code=400, detail="Ability mofidiers not assigned")
    dexterity_modifier = get_output("get_ability_modifier")['data']['dexterity']
    if not get_output("get_initiative"):
        speed = {"initiative": dexterity_modifier} 
        store_output("get_initiative", speed)
    output_initiative = get_output("get_initiative")
    return output_initiative

@app.get("/speed")
def get_speed():
    if not get_output("get_race") and get_output("get_race_context"):
        raise HTTPException(status_code=400, detail="Race and RAce Context not assigned")
    race = get_output("get_race")
    race_context = get_output("get_race_context")
    if not get_output("get_speed"):
        speed = inf.get_speed(race, race_context)
        store_output("get_speed", speed)
    output_speed = get_output("get_speed")
    return output_speed

@app.get("/all")
def get_all():
    get_race()
    get_race_context()
    # get_class()
    # get_background()
    # get_class_context()
    # get_background_context()
    # get_abilities()
    # get_ability_scores()
    # get_ability_modifier()
    # prof = get_proficiency_modifier()
    # get_proficiencies_languages()
    # get_attacks()
    # get_armor_class()
    # get_initiative()
    output = get_speed()
    return output
