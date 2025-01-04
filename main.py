from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from inference_pipeline import inference_methods

inf = inference_methods.dndCharacter()

app = FastAPI()

sessions = {}
    
@app.get("/race")
def get_race():
    return {"race": inf.get_race()}

@app.get("/class")
def get_class():
    return {"class": inf.get_class()}

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
