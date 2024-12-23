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