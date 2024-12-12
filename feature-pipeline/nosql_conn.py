from pymongo import MongoClient, errors
import os

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

collection = db["backgrounds"]

base_name = 'C://Users//rajes//Documents//GitHub//dungeons-and-dragons-game//web_scraping//backgrounds'
files = os.listdir(base_name)

for file in files:
    file_name = file.replace('.txt', '')

    with open(base_name + '//' + file, 'r', encoding='utf-8') as f:
        data = f.read()

    doc = {"name": file_name, "description": data}

    collection.insert_one(doc)

    print("record " + file_name + " inserted into " + base_name.split('//')[-1])
