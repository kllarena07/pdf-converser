from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import tempfile

def split_pdf(contents: bytes, filename: str) -> List[Document]:
    just_filename = filename[:-4]
    with tempfile.NamedTemporaryFile(delete=True) as temp:
      temp.write(contents)
      temp.flush()

      loader = PyPDFLoader(temp.name)
      data = loader.load()

      text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
      docs = text_splitter.split_documents(data)
      
      for doc in docs:
          doc.metadata["filename"] = just_filename
      
      return docs