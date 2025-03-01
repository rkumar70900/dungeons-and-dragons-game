import random
from pymongo import MongoClient, errors
import pandas as pd
from thefuzz import process

class dependencies():
    def __init__(self):
        pass
    
    def roll_dice(self, total_faces, number_of_dices):
        rolls = [random.randint(1, total_faces) for _ in range(number_of_dices)]
        return rolls
    
    def drop_low_sum(self, total_faces, number_of_dices):
        rolls = self.roll_dice(total_faces, number_of_dices)
        rolls.remove(min(rolls))
        total = sum(rolls)
        return total
    
    def connect_mongo(self):
        try:
            # Attempt connection
            client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
            # Force connection check
            client.admin.command("ping")
            print("Connected to MongoDB!")
            return client
        except errors.ServerSelectionTimeoutError as err:
            print("Error: Could not connect to MongoDB")
            print(err)
    
    def get_context_collection(self, client, collection_name):
        db = client["context_data"]
        collection = db[collection_name]
        return collection
    
    def get_distinct_names(self, collection):
        distinct_names = collection.distinct("name")
        return distinct_names
    
    def get_ability_modifier(self, ability_score):
        if 2 <= ability_score <= 3:
            return -4
        elif 4 <= ability_score <= 5:
            return -3
        elif 6 <= ability_score <= 7:
            return -2
        elif 8 <= ability_score <= 9:
            return -1
        elif 10 <= ability_score <= 11:
            return 0
        elif 12 <= ability_score <= 13:
            return 1
        elif 14 <= ability_score <= 15:
            return 2
        elif 16 <= ability_score <= 17:
            return 3
        elif 18 <= ability_score <= 19:
            return 4
        elif 20 <= ability_score <= 21:
            return 5
        else:
            raise ValueError("Ability score must be between 2 and 21.")
    
    def calculate_attack_modifier_damage(self, weapon_type, dexterity_modifier, strength_modifier, proficiency_modifier, property):
        if "finesse" in property:
            attack_modifier = max(dexterity_modifier, strength_modifier) + proficiency_modifier
            damage = max(dexterity_modifier, strength_modifier)
            return attack_modifier, damage
        if weapon_type == "ranged":
            attack_modifier = dexterity_modifier + proficiency_modifier
            damage = dexterity_modifier
            return attack_modifier, damage
        if weapon_type == "melee":
            attack_modifier = strength_modifier + proficiency_modifier
            damage = strength_modifier
            return attack_modifier, damage
    
    def get_data(self, client, collection_name):
        db = client["context_data"]
        collection = db[collection_name]
        df = pd.DataFrame(list(collection.find()), dtype=str)
        return df
    
    def lower_case_list(self, lst):
        return [item.lower() for item in lst]

    def filter_dataframe(self, df, weapon_list, column_name, threshold=80):

        matched_weapons = set()
        
        for weapon in weapon_list:
            best_match, score = process.extractOne(weapon, df[column_name].tolist(), score_cutoff=threshold)
            if best_match:
                matched_weapons.add(best_match)
        
        return df[df[column_name].isin(matched_weapons)]

    def character_weapons(self, client, weapons):
        weapons_df = self.get_data(client, "weapons")
        weapons_df = self.filter_dataframe(weapons_df, weapons, "weapon_name")
        return weapons_df
    
    def character_armor(self, client, armor):
        armor_df = self.get_data(client, "armor")
        armor_df = self.filter_dataframe(armor_df, armor, "armor")
        return armor_df
    



