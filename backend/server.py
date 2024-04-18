import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from pymongo import MongoClient
from split_pdf import split_pdf
from pydantic import BaseModel

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "langchain-gemini"
COLLECTION_NAME = "vectors"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

EMBEDDING_FIELD_NAME = "embeddings"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

app = FastAPI()

class ExtractionMsg(BaseModel):
    """Schema for the response message after extract POST method is called"""
    filename: str
    message: str
    embeddings_successful: bool
    resync: bool

@app.post("/extract/")
async def extract_text(pdf: UploadFile = File(...)) -> ExtractionMsg:
    """Extracts text from a PDF, embed it, and insert into the database."""
    contents = await pdf.read()
    filename = pdf.filename
    just_filename = filename[:-4]

    collection_to_list = list(collection.find({ "filename": just_filename }))
    docs = split_pdf(contents, filename)
    resync=False

    if len(collection_to_list) == len(docs):
        return {
            "filename": just_filename,
            "message": "Document already exists in the database.",
            "embeddings_successful": False,
            "resync": resync
        }

    if len(collection_to_list) != 0 and len(collection_to_list) != len(docs):
        collection.delete_many({ "filename": just_filename })
        print(f"""
            WARNING: Document lengths do not match.
            
            Deleting all documents with the filename: {just_filename} to resync the database.
        """)
        resync=True

    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=gemini_embeddings,
        collection=collection,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
    )

    return {
        "filename": just_filename,
        "message": "Document successfully extracted, embedded, and inserted into the database.",
        "embeddings_successful": True,
        "was_resynced": resync
    }

class UserQuery(BaseModel):
    query: str

@app.post("/query/")
async def query_pdf(user_query: UserQuery):
    return { "query": user_query.query }