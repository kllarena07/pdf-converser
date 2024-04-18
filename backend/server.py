import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
import tempfile
from pymongo import MongoClient

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import MongoDBAtlasVectorSearch

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "langchain-gemini"
COLLECTION_NAME = "vectors"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

EMBEDDING_FIELD_NAME = "embeddings"
client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

app = FastAPI()

@app.post("/extract/")
async def extract_text(pdf: UploadFile = File(...)):
    contents = await pdf.read()
    filename = pdf.filename
    just_filename = filename.split(".")[0]
    shortened_filename = f'pdf_{just_filename.lower().replace(" ", "_")[:5]}'
    
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        temp.write(contents)
        temp.flush()

        loader = PyPDFLoader(temp.name)
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(data)
        
        for doc in docs:
            doc.metadata["filename"] = shortened_filename

        gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        MongoDBAtlasVectorSearch.from_documents(
            documents=docs,
            embedding=gemini_embeddings,
            collection=collection,
            index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
        )
        
        return {
            "filename": shortened_filename,
            "embeddings_successful": True
        }
