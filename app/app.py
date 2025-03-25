import whisper
import tempfile
import os
from fastapi import FastAPI, File, UploadFile
from transformers import pipeline
import torch
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import requests
import sys
sys.path.append('/workspace/app')
import workflow_manager
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global variable to store the latest emotion scores
latest_emotion_scores = {}

# Load models
whisper_model = whisper.load_model("base")
emotion_classifier = pipeline(
    "text-classification", 
    model="joeddav/distilbert-base-uncased-go-emotions-student", 
    top_k=None,
    device=0  # Use GPU explicitly
)

# Ensure the client directory exists
if not os.path.exists("client"):
    os.makedirs("client", exist_ok=True)
    print("Created client directory")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main application HTML page."""
    try:
        # Use the absolute path based on the location of app.py
        app_dir = os.path.dirname(os.path.abspath(__file__))
        index_path = os.path.join(app_dir, "client", "index.html")
        
        print(f"Looking for index.html at absolute path: {index_path}")
        
        if os.path.exists(index_path):
            print("Found index.html file")
            with open(index_path, "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            print(f"ERROR: index.html not found at {index_path}")
            return HTMLResponse(content=f"<h1>Error: index.html not found</h1><p>Looked at: {index_path}</p>")
    except Exception as e:
        print(f"Error serving index.html: {e}")
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>")

@app.post("/transcribe_and_generate")
async def transcribe_and_generate(file: UploadFile = File(...)):
    """
    Transcribes an audio file and detects emotions.
    Updates the global latest_emotion_scores.
    """
    global latest_emotion_scores

    # Save the uploaded audio file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp_filename = tmp.name
        content = await file.read()
        tmp.write(content)
    
    # Transcribe using Whisper
    result = whisper_model.transcribe(tmp_filename)
    text = result["text"]
    
    # Delete the temporary file
    os.remove(tmp_filename)
    
    # Run emotion classification on the transcription
    emotions = emotion_classifier(text)
    # Assume emotions[0] is a list of dictionaries, each with keys "label" and "score"
    emotion_results = {e["label"]: e["score"] for e in emotions[0]}
    
    # Update the global emotion scores
    latest_emotion_scores = emotion_results
    
    # Silently trigger the workflow without affecting other functionality
    try:
        requests.post("http://127.0.0.1:8010/trigger_workflow", timeout=0.1)
    except:
        pass
    
    return {
        "transcription": text,
        "emotions": emotion_results
    }

@app.get("/get_emotion_data")
async def get_emotion_data():
    """
    Return the latest emotion data for the ComfyUI custom node to consume.
    """
    return {"emotions": latest_emotion_scores}

@app.post("/trigger_workflow")
async def trigger_workflow():
    """
    Trigger the ComfyUI workflow to generate an image based on the latest emotions.
    """
    try:
        # Use the function from workflow_manager instead of importing it
        comfyui_url = workflow_manager.test_comfyui_connection()
        thread = workflow_manager.run_workflow_with_custom_nodes(comfyui_url)
        return {"status": "success", "message": "Workflow triggered successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# Static file serving with absolute path
app_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(app_dir, "client")
app.mount("/client", StaticFiles(directory=client_dir), name="client")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)