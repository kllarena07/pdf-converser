import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from pymongo import MongoClient
from split_pdf import split_pdf
from pydantic import BaseModel

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "langchain-gemini"
COLLECTION_NAME = "vectors"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

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

    # just check for which documents aren't added and add them instead of deleting the whole thing
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
    filename: str

@app.post("/query/")
async def query_pdf(user_query: UserQuery):
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_search = MongoDBAtlasVectorSearch(collection=collection, embedding=gemini_embeddings, index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME)

    # need to omit _id from returned documents
    qa_retriever = vector_search.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 200,
            "filter": {
                "filename": user_query.filename
            },
            "post_filter_pipeline": [{ "$limit": 25 }]
        }
    )
    
    prompt_template = """
        Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        {context}
        
        Question: {question}
    """
    
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro")
    
    qa = RetrievalQA.from_chain_type(llm=gemini_llm,chain_type="stuff", retriever=qa_retriever, return_source_documents=True, chain_type_kwargs={"prompt": PROMPT})
    
    docs = qa({"query": user_query.query})
    
    return { "query": user_query.query, "result": docs["result"] }

class DeleteQuery(BaseModel):
    filename: str

@app.post("/deleteAll/")
async def delete_all(filename: DeleteQuery):
    collection.delete_many({ "filename": filename.filename })
    return { "message": f"All documents with the filename: {filename.filename} have been deleted." }