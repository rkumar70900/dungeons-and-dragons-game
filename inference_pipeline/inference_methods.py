from inference_pipeline import dep
import re
import random
from training_pipeline import ask_llm

class dndCharacter():
    def __init__(self):
        self.dep = dep.dependencies()
        self.ask = ask_llm.askLLM()
        self.abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        self.ability_skills = {"dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"], 
                           "intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"], 
                           "wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"], 
                           "charisma": ["Deception", "Intimidation", "Performance", "Persuasion"], 
                           "strength": ["Athletics"], 
                           "constitution": [] }
        self.skills = ["Acrobatics", "Sleight of Hand", "Stealth", "Arcana", "History", "Investigation", "Nature", "Religion",
                       "Animal Handling", "Insight", "Medicine", "Perception", "Survival", "Deception", "Intimidation", "Performance", "Persuasion",
                       "Athletics"]
        self.client = self.dep.connect_mongo()

    def ability_scores(self):
        raw_scores = [self.dep.drop_low_sum(6, 4) for _ in range(6)]
        sorted_raw_scores = sorted(raw_scores, reverse=True)
        return sorted_raw_scores
    
    def get_abilities(self, class_name, class_context):
        class_abilities = self.ask.get_abilities(class_name, class_context)
        return class_abilities
    
    def assign_scores(self, class_abilities):
        matches = [attr for attr in self.abilities if re.search(rf'\b{attr}\b', class_abilities, re.IGNORECASE)]
        non_matches = [attr for attr in self.abilities if attr not in matches]
        random.shuffle(non_matches)
        scores = self.ability_scores()
        assigned_scores = {
            attr: scores[i] for i, attr in enumerate(matches + non_matches)
        }
        return assigned_scores
    
    def get_race(self):
        collection = self.dep.get_context_collection(self.client, "races")
        races = self.dep.get_distinct_names(collection)
        current_choice = random.choice(races)
        return current_choice
    
    def get_class(self):
        collection = self.dep.get_context_collection(self.client, "classes")
        classes = self.dep.get_distinct_names(collection)
        current_choice = random.choice(classes)
        return current_choice
    
    def get_background(self):
        collection = self.dep.get_context_collection(self.client, "backgrounds")
        backgrounds = self.dep.get_distinct_names(collection)
        current_choice = random.choice(backgrounds)
        return current_choice

    def get_class_context(self, class_name):
        class_context = self.ask.extract_context("classes", class_name)
        return class_context

    def get_race_context(self, race_name):
        race_context = self.ask.extract_context("races", race_name)
        return race_context

    def get_background_context(self, background_name):
        background_context = self.ask.extract_context("backgrounds", background_name)
        return background_context
    
    def ability_modifier(self, strength, dexterity, constitution, intelligence, wisdom, charisma):
        ability_modifier = {}
        ability_modifier['strength'] = self.dep.get_ability_modifier(strength)
        ability_modifier['dexterity'] = self.dep.get_ability_modifier(dexterity)
        ability_modifier['constitution'] = self.dep.get_ability_modifier(constitution)
        ability_modifier['intelligence'] = self.dep.get_ability_modifier(intelligence)
        ability_modifier['wisdom'] = self.dep.get_ability_modifier(wisdom)
        ability_modifier['charisma'] = self.dep.get_ability_modifier(charisma)
        return ability_modifier
    
    def proficiency_modifier(self):
        proficiency = {"proficiency_modifier": 2}
        return proficiency
    
    def saving_throws(self, class_name, class_context, ability_scores, proficiency_modifier):
        saving_throws_scores = {}
        class_saving_throws = self.ask.get_saving_throws(class_name, class_context)
        matches = [attr for attr in self.abilities if re.search(rf'\b{attr}\b', class_saving_throws, re.IGNORECASE)]
        non_matches = [attr for attr in self.abilities if attr not in matches]
        for match in matches:
            saving_throws_scores[match] = ability_scores[match] + proficiency_modifier
        for non_match in non_matches:
            saving_throws_scores[non_match] = ability_scores[non_match]
        return saving_throws_scores
    
    def get_skills(self, class_name, background_name, class_context, background_context, ability_scores, proficiency_modifier):
        skill_scores = {}
        class_skills = self.ask.get_skills(class_name, background_name, class_context, background_context)
        matches = [attr for attr in self.skills if re.search(rf'\b{attr}\b', class_skills, re.IGNORECASE)]
        for key, value in self.ability_skills.items():
            if any(val in value for val in matches):
                for val in value:
                    skill_scores[val] = ability_scores[key] + proficiency_modifier
            else:
                for val in value:
                    skill_scores[val] = ability_scores[key]
        return skill_scores


