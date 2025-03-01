from inference_pipeline.inference_methods import dndCharacter
from inference_pipeline.dep import dependencies

inf = dndCharacter()
dep = dependencies()

weapons = ["long sword", "Maul"]

client = inf.client
df = dep.character_weapons(client, weapons)

print(df)