from pymongo import MongoClient, errors

try:
    # Attempt connection
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    # Force connection check
    client.admin.command("ping")
    print("Connected to MongoDB!")
except errors.ServerSelectionTimeoutError as err:
    print("Error: Could not connect to MongoDB")
    print(err)

db = client["context_data"]

collection = db["classes"]

name = "alchemist"

with open(".//classes//alchemist.txt") as file:
    data = file.read()

doc = {"name": name, "description": data}

collection.insert_one(doc)

for doc in collection.find():
    print(doc)