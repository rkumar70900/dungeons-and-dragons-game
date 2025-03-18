
"""
This module provides functionality to connect to a MongoDB database, fetch data from a specified collection,
chunk the data into manageable pieces, and create or update an index in Marqo with the chunked data.

Functions:
    fetch_and_chunk_data(collection_name):
        Fetches data from a specified MongoDB collection and chunks it for Marqo indexing.
    create_or_update_index(index_name, chunks, batch_size=128):
        Creates or updates a Marqo index with the provided data chunks.
    delete_index(index_name):
        Deletes a specified Marqo index.

Constants:
    MAX_TOKENS (int): The maximum number of tokens for chunking content.
"""

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
    Fetch data from a MongoDB collection and chunk it for processing.
    Args:
        collection_name (str): The name of the MongoDB collection to fetch data from.
    Returns:
        list: A list of dictionaries, each containing a chunk of the document's content, 
              the document's title, and the document's ID.
    Each dictionary in the returned list has the following structure:
        {
            "Title": str,        # The name of the document
            "content": str,      # A chunk of the document's description
            "document_id": str   # The ID of the document
        }
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
    Creates a new index or updates an existing index with the provided chunks of documents.

    Args:
        index_name (str): The name of the index to create or update.
        chunks (list): A list of document chunks to be added to the index.
        batch_size (int, optional): The number of documents to process in each batch. Defaults to 128.

    Raises:
        MarqoApiError: If there is an error creating the index.

    Note:
        If the index already exists, it will catch the MarqoApiError and proceed to update the index with the new documents.
    """
    try:
        mq_client.create_index(index_name, model="hf/e5-base-v2" )
    except MarqoApiError:
        print(f"Index '{index_name}' already exists. Proceeding to update...")
    mq_client.index(index_name).add_documents(chunks, tensor_fields=['content', 'Title'], client_batch_size=batch_size)

chunks = fetch_and_chunk_data("races")
create_or_update_index("races", chunks)

def delete_index(index_name):
    """
    Deletes an index from the vector database.

    Args:
        index_name (str): The name of the index to be deleted.

    Raises:
        Exception: If there is an error during the deletion process.

    Example:
        delete_index("example_index")
    """
    try:
        mq_client.index(index_name).delete()
        print(f"Index '{index_name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting index '{index_name}': {e}")

