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
    
    def ability_modifier(self, ability_scores):
        ability_modifier = {}
        ability_modifier['strength'] = self.dep.get_ability_modifier(ability_scores["strength"])
        ability_modifier['dexterity'] = self.dep.get_ability_modifier(ability_scores["dexterity"])
        ability_modifier['constitution'] = self.dep.get_ability_modifier(ability_scores["constitution"])
        ability_modifier['intelligence'] = self.dep.get_ability_modifier(ability_scores["intelligence"])
        ability_modifier['wisdom'] = self.dep.get_ability_modifier(ability_scores["wisdom"])
        ability_modifier['charisma'] = self.dep.get_ability_modifier(ability_scores["charisma"])
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
    
    def get_passive_perception(self, perception):
        passive_perception = 10 + perception
        return passive_perception
    
    def get_proficiencies_languages(self, class_name, background_name, class_context, background_context):
        proficiencies = self.ask.get_proficiencies_languages(class_name, background_name, class_context, background_context)
        return proficiencies
    
    def get_equipment_money(self, class_name, background_name, class_context, background_context):
        equipment_money = self.ask.get_equipment_money(class_name, background_name, class_context, background_context)
        return equipment_money
    
    def get_attacks_damage(self, weapons, dexterity_modifier, strength_modifier, proficiency_modifier):
        attacks = []
        weapons_df = self.dep.character_weapons(self.client, weapons)
        for i in range(len(weapons_df)):
            weapon = weapons_df.iloc[i]["weapon_name"]
            damage = weapons_df.iloc[i]["damage"].split(" ")
            weapon_type = weapons_df.iloc[i]["weapons_type"]
            property = weapons_df.iloc[i]["properties"]
            attack_modifier, damage_score = self.dep.calculate_attack_modifier_damage(weapon_type, dexterity_modifier, strength_modifier, proficiency_modifier, property)
            damage = damage[0] + " " + str(damage_score) + " " + damage[1]
            attacks.append({"weapon": weapon, "attack_modifier": attack_modifier, "damage": damage})
        return attacks
    
    def get_armor_class(self, armor, dexterity_modifier):
        if not armor:
            return 10 + dexterity_modifier
        armor_df = self.dep.character_armor(self.client, armor)
        print(armor_df)
        armor_type = armor_df.iloc[0]["armor_type"]
        armor_class = int(armor_df.iloc[0]["armor_class"][:2])
        if armor_type == 'light':
            return armor_class + dexterity_modifier
        elif armor_type == 'medium':
            return armor_class + min(dexterity_modifier, 2)
        elif armor_type == 'heavy':
            return armor_class

    def get_speed(self, race_name, race_context):
        speed = self.ask.get_speed(race_name, race_context)
        return speed




    

