from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from inference_pipeline import inference_methods

inf = inference_methods.dndCharacter()

app = FastAPI()

sessions = {}

class SessionData(BaseModel):
    character_class: Optional[str] = None
    
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

