# file_upload.py
from fastapi import APIRouter, File, UploadFile, Depends
from langchain_google_genai import ChatGoogleGenerativeAI
from utils import pdf_load_and_split, QA_Chain_Retrieval, pincone
import tempfile
import os
from langchain.schema import Document
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import get_db
load_dotenv()

router = APIRouter(prefix="/file", tags=["user_file"]) 

@router.post("/upload_file/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # File name ko . (dot) ke basis par todta hai aur list bana deta hai.
    file_extension = file.filename.split(".")[-1].lower()
# Purpose: Temporary file create karna.# Returns two things:# fd → file descriptor (ek integer jo OS ko file ko refer karne ke liye chahiye)
# tmp_file_path → Temporary file ka path (location on disk)# suffix=f".{file_extension}"# Temporary file ka extension wahi rakhta hai jo user ki file ka extension hai.
# Example: agar file_extension = "pdf" → file ka naam tmp1234.pdf jaisa ho sakta hai.
    fd, tmp_file_path = tempfile.mkstemp(suffix=f".{file_extension}")
    # Temporary file is made to safely store uploaded data for processing without affecting original files.
    with os.fdopen(fd, 'wb') as tmp_file:
        tmp_file.write(contents)
# tempfile.mkstemp() → Temporary file create, return fd & tmp_file_path# os.fdopen(fd, 'wb') → File descriptor ko Python file object me convert
# # with → File safely open karna aur auto-close# tmp_file.write(contents) → File me data write karna
    if file_extension == "pdf":
        data = pdf_load_and_split(tmp_file_path)
        all_chunks = [doc.page_content for doc in data] # Correctly extract page content
# all_chunks:["Hello world", "This is LangChain"] 
    else:
        raise TypeError("Not supported file format")

    vectorstore = pincone()
    documents = [Document(page_content=chunk) for chunk in all_chunks]
    all_data = vectorstore.add_documents(documents)
# all_data (stored in vectorstore):# [
#   {id: "1", embedding: [...], content: "Hello world"},
#   {id: "2", embedding: [...], content: "This is LangChain"}]
    return {"status": "success", "data": all_data}

import os as _os
GEMINI_API_KEY = _os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_API_KEY, temperature=0)

@router.post("/retrieve")
async def retrieve(query: str, user_id: int, patient_id: int, db: Session = Depends(get_db)):
    """
    Retrieves information and saves chat history.
    Args:
        query (str): The user's question.
        user_id (int): The ID of the user.
        patient_id (int): The ID of the patient.
        db (Session): The database session dependency.
    """

    vectorstore = pincone()
    
    # Pass all necessary data to the RAG function
    results = QA_Chain_Retrieval(
        question=query, 
        patient_id= patient_id, 
        user_id= user_id,  
        vector_store=vectorstore, 
        gini_llm=llm, 
        db=db, 

    )
    return results

