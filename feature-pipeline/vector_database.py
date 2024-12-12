from pymongo import MongoClient, errors
import os
from textwrap import wrap
import marqo
from marqo.errors import MarqoApiError
MAX_TOKENS = 3000

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

mq_client = marqo.Client(url='http://localhost:8882')


def fetch_and_chunk_data(collection_name):
    """
    Fetch data from MongoDB and chunk it for Marqo.
    """
    collection = db[collection_name]
    documents = collection.find()
    chunks = []
    
    for doc in documents:
        content = str(doc["description"])  # Serialize MongoDB document
        # Split content into manageable chunks
        for chunk in wrap(content, width=MAX_TOKENS):
            chunks.append({
                "Title": doc["name"],
                "content": chunk,
                "document_id": str(doc.get("_id"))
            })
    return chunks

def create_or_update_index(index_name, chunks, batch_size=128):
    """
    Create or update Marqo index with data chunks.
    """
    try:
        # Create index if it doesn't exist
        mq_client.create_index(index_name, model="hf/e5-base-v2" )
    except MarqoApiError:
        print(f"Index '{index_name}' already exists. Proceeding to update...")
    

    mq_client.index(index_name).add_documents(chunks, tensor_fields=['content', 'Title'], client_batch_size=batch_size)

chunks = fetch_and_chunk_data("races")
create_or_update_index("races", chunks)

# results = mq_client.index("classes").search(
#     q="information about alchemist", search_method='LEXICAL', limit=4
# )
# print(results)

def delete_index(index_name):
    """
    Deletes a Marqo index.

    :param index_name: Name of the index to delete.
    """
    try:
        mq_client.index(index_name).delete()
        print(f"Index '{index_name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting index '{index_name}': {e}")

# delete_index("backgrounds")
