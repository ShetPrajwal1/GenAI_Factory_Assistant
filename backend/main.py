from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
import time

# Import our custom modules
from backend.stt import transcribe_audio
from backend.rag import retrieve_context, ingest_historical_data
from backend.llm import extract_structured_issue

app = FastAPI(title="Voice-Based Factory Maintenance Assistant API")

# Allow Streamlit to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/temp", exist_ok=True)

class HistoryQuery(BaseModel):
    query: str
    top_k: int = 3

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    """
    1. Saves uploaded audio to a temp file.
    2. Transcribes the audio using faster-whisper.
    3. Retrieves context from FAISS based on the transcript.
    4. Submits transcript + context to Ollama for structured extraction.
    5. Returns the combined result.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    temp_file_path = f"data/temp/{uuid.uuid4()}_{file.filename}"
    
    try:
        # 1. Save File
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Transcribe
        t0 = time.time()
        transcript = transcribe_audio(temp_file_path)
        t1 = time.time()
        
        # 3. Retrieve Context
        past_context = retrieve_context(transcript)
        t2 = time.time()
        
        # 4. Extract Structured Issue via LLM
        structured_data = extract_structured_issue(transcript, past_context)
        t3 = time.time()
        
        return {
            "transcript": transcript,
            "retrieved_context": past_context,
            "analysis": structured_data,
            "metrics": {
                "transcription": round(t1 - t0, 1),
                "retrieval": round(t2 - t1, 1),
                "llm": round(t3 - t2, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/query-history")
async def query_history(request: HistoryQuery):
    """
    Allows text-based querying of the maintenance history.
    """
    try:
        context = retrieve_context(request.query, request.top_k)
        return {"context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest-data")
async def ingest_data(filename: str):
    """
    Endpoint to trigger data ingestion from a CSV file in the data folder.
    e.g., filename='data/mock_logs.csv'
    """
    try:
        ingest_historical_data(filename)
        return {"status": "success", "message": f"Ingested data from {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
