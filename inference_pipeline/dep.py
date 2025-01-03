import random
from pymongo import MongoClient, errors

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