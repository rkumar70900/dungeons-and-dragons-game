from inference_pipeline import dep
import re
import random
from training_pipeline import ask_llm

class dndCharacter():
    def __init__(self):
        self.dep = dep.dependencies()
        self.ask = ask_llm.askLLM()
        self.abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        self.client = self.dep.connect_mongo()

    def ability_scores(self):
        raw_scores = [self.dep.drop_low_sum(6, 4) for _ in range(6)]
        sorted_raw_scores = sorted(raw_scores, reverse=True)
        return sorted_raw_scores
    
    def assign_scores(self, class_name):
        class_abilities = self.ask.get_abilities(class_name)
        matches = [attr for attr in self.abilities if re.search(rf'\b{attr}\b', class_abilities, re.IGNORECASE)]
        non_matches = [attr for attr in self.abilities if attr not in matches]
        random.shuffle(non_matches) 
        scores = self.ability_scores()
        print(scores)
        assigned_scores = {
            attr: scores[i] for i, attr in enumerate(matches + non_matches)
        }
        return assigned_scores
    
    def get_race(self):
        collection = self.dep.get_context_collection(self.client, "races")
        return self.dep.get_distinct_names(collection)
    
    def get_class(self):
        collection = self.dep.get_context_collection(self.client, "classes")
        return self.dep.get_distinct_names(collection)
    
    def get_background(self):
        collection = self.dep.get_context_collection(self.client, "backgrounds")
        return self.dep.get_distinct_names(collection)


