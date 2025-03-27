from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pymongo import MongoClient
from pypdf import PdfReader, PdfWriter
import os

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["context_data"]
collection = db["audit_logs"]

PDF_PATH = "C://Users//rajes//Downloads//5E_CharacterSheet_Fillable.pdf"
# OUTPUT_PATH = "/mnt/data/filled_character_sheet.pdf"

session_id = '0bc21819-5fdb-4b54-b09e-734fbf5deeb6'

def fill_pdf_pypdf(session_id: str):
    """Fill a PDF using pypdf."""
    
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"Input PDF file '{PDF_PATH}' does not exist.")

    # Retrieve data from MongoDB
    session_entries = list(collection.find({"session_id": session_id}))
    if not session_entries:
        raise ValueError(f"No data found for session_id: {session_id}")

    # Merge multiple entries
    merged_data = {}
    for entry in session_entries:
        merged_data.update(entry)

    # Load PDF
    reader = PdfReader(PDF_PATH)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i == 0:  # Fill only first page
            for field in page.annotations or []:
                field_name = field.get("/T")
                print(field_name)


fill_pdf_pypdf(session_id)