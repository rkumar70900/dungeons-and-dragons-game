from inference_pipeline import dep
import re
import random
from training_pipeline import ask_llm

class dndCharacter():
    def __init__(self):
        self.dep = dep.dependencies()
        self.ask = ask_llm.askLLM("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")
        self.abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

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
