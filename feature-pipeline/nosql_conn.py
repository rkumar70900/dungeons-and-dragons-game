from pymongo import MongoClient, errors
"""
This script connects to a MongoDB database, reads text files from a specified directory,
and inserts the contents of these files into a MongoDB collection.
Modules:
    pymongo: Provides tools for working with MongoDB.
    os: Provides functions for interacting with the operating system.
Functions:
    None
Attributes:
    client (MongoClient): The MongoDB client instance.
    db (Database): The MongoDB database instance.
    collection (Collection): The MongoDB collection instance.
    base_name (str): The base directory path where the text files are located.
    files (list): List of files in the base directory.
Exceptions:
    errors.ServerSelectionTimeoutError: Raised if the connection to MongoDB times out.
Usage:
    Run the script to connect to MongoDB, read text files from the specified directory,
    and insert the file contents into the MongoDB collection.
"""
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

base_name = 'C://Users//rajes//Documents//GitHub//dungeons-and-dragons-game//feature-pipeline//armor.csv'
files = os.listdir(base_name)

for file in files:
    file_name = file.replace('.txt', '')

    with open(base_name + '//' + file, 'r', encoding='utf-8') as f:
        data = f.read()

    doc = {"name": file_name, "description": data}

    collection.insert_one(doc)

    print("record " + file_name + " inserted into " + base_name.split('//')[-1])


