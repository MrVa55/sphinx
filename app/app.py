"""
Sphinx API Server - Main Application

This FastAPI application provides the backend for the Sphinx emotional projection system.
It connects the frontend interfaces with the ComfyUI image/video generation system.

The API is organized into these main sections:
1. Page-serving endpoints - Serve HTML interfaces
2. Audio processing endpoints - Transcribe and analyze speech
3. Emotion and transformation endpoints - Process and store emotional states
4. Workflow management endpoints - Handle ComfyUI workflows
5. Media endpoints - Manage generated images and videos
6. System endpoints - API status and diagnostics
"""

import whisper
import tempfile
import os
import logging
from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Depends
from transformers import pipeline
import torch
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import requests
import sys
sys.path.append('/workspace/app')
import workflow_manager
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import json
import time
from typing import Callable
import inspect
from functools import wraps
from pydantic import BaseModel
import re

#########################################
# CONFIGURATION AND SETUP
#########################################

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api.log")
    ]
)
logger = logging.getLogger("sphinx-api")

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

# Global variables
latest_emotion_scores = {}
cache_dir = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(cache_dir, exist_ok=True)

# Create API logging dependency
async def log_api_call(request: Request):
    """
    Dependency that logs information about the API call.
    Use with Depends() in route functions.
    """
    # Get the calling function name
    frame = inspect.currentframe().f_back
    function_name = frame.f_code.co_name if frame else "unknown_function"
    
    # Log route and method
    logger.info(f"API call: {request.method} {request.url.path} → {function_name}")
    
    # Log query parameters
    if request.query_params:
        logger.info(f"Query params: {dict(request.query_params)}")
    
    # For POST/PUT, we used to try to log body content but that consumes the request body
    # Now we just log that there is a request body but don't consume it
    if request.method in ("POST", "PUT"):
        logger.info("Request has a body (not logged to avoid consuming it)")
    
    return None  # This dependency doesn't modify the request

# Load models
whisper_model = whisper.load_model("base")
emotion_classifier = pipeline(
    "text-classification", 
    model="joeddav/distilbert-base-uncased-go-emotions-student", 
    top_k=None,
    device=0  # Use GPU explicitly
)

# Add LLM for transformation analysis
from transformers import pipeline

# Initialize a text-generation model for transformation analysis
try:
    # Use a smaller model for efficiency
    text_generator = pipeline("text-generation", 
                             model="distilgpt2", 
                             device=0 if torch.cuda.is_available() else -1)
except Exception as e:
    logger.warning(f"Could not load text generation model: {e}")
    text_generator = None

# Transformation options - KEEP THIS! It's used by the LLM to select transformations
TRANSFORMATIONS = [
    {"from": "Closed off", "to": "Open"},
    {"from": "Stagnant", "to": "Creative"},
    {"from": "Fearful", "to": "Trusting"},
    {"from": "Hiding", "to": "Visible"},
    {"from": "Uncentered", "to": "Centered"},
    {"from": "Silenced", "to": "Honest"},
    {"from": "Disassociated", "to": "Embodied"},
    {"from": "Ruminating", "to": "Present"},
    {"from": "Hypervigilant", "to": "Relaxed"},
    {"from": "Illness", "to": "Health"},
    {"from": "Oppression", "to": "Freedom"},
    {"from": "Scarcity", "to": "Abundance"},
    {"from": "Controlling", "to": "Flexible"},
    {"from": "Codependent", "to": "Authentic Autonomy"},
    {"from": "Feeling Excluded", "to": "Belonging"},
    {"from": "Safety & Comfort", "to": "Embracing Transformation"},
    {"from": "Shame", "to": "Healthy Pride"},
    {"from": "External Validation", "to": "Wholeness"},
    {"from": "Controlling My Body", "to": "Listening to My Body"}
]

# Request models
class TransformationRequest(BaseModel):
    transformation: dict = None

class EmotionRequest(BaseModel):
    emotions: dict = None

class TextRequest(BaseModel):
    text: str = ""

# Ensure client directory exists
if not os.path.exists("client"):
    os.makedirs("client", exist_ok=True)
    print("Created client directory")

# Add at the top with other global variables
active_workflow = None

class TransformationRequest(BaseModel):
    transformation: dict = None



#########################################
# 1. PAGE-SERVING ENDPOINTS
#########################################

@app.get("/", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def get_index():
    """Serves the projection experience as the main entry point"""
    try:
        # Use the absolute path based on the location of app.py
        app_dir = os.path.dirname(os.path.abspath(__file__))
        projection_path = os.path.join(app_dir, "client", "projection.html")
        
        if os.path.exists(projection_path):
            with open(projection_path, "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content=f"<h1>Error: projection.html not found</h1>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>")

@app.get("/gui", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def get_gui():
    """Serves the GUI dashboard"""
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(app_dir, "client", "gui.html")
        
        if os.path.exists(gui_path):
            with open(gui_path, "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content=f"<h1>Error: gui.html not found</h1>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>")

@app.get("/workflow_manager", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def serve_workflow_manager():
    """Serves the workflow manager interface"""
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(app_dir, "client", "workflow_manager.html")
        
        if os.path.exists(gui_path):
            with open(gui_path, "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content=f"<h1>Error: workflow_manager.html not found</h1>")
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1><pre>{error_traceback}</pre>")

@app.get("/client/script.js", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def get_script_js():
    """Serves the script.js file"""
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(app_dir, "client", "script.js")
        
        if os.path.exists(script_path):
            with open(script_path, "r") as f:
                js_content = f.read()
            return HTMLResponse(content=js_content, media_type="application/javascript")
        else:
            return HTMLResponse(content="console.error('script.js not found');", 
                               media_type="application/javascript", 
                               status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"console.error('Error loading script: {str(e)}');", 
                           media_type="application/javascript", 
                           status_code=500)

# Static file serving
app_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(app_dir, "client")
app.mount("/client", StaticFiles(directory=client_dir), name="client")

#########################################
# 2. AUDIO PROCESSING ENDPOINTS
#########################################

@app.post("/transcribe", dependencies=[Depends(log_api_call)])
async def transcribe(file: UploadFile = File(...)):
    """Transcribe audio file to text"""
    try:
        # Save the uploaded file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(await file.read())
        temp_file.close()
        
        # Transcribe the audio
        result = whisper_model.transcribe(temp_file.name)
        transcription = result["text"]
        logger.info(f"Transcription: {transcription}")
        
        # Save the transcription for reference
        cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        with open(os.path.join(cache_dir, "last_transcription.txt"), "w") as f:
            f.write(transcription)
        
        # Clean up
        os.unlink(temp_file.name)
        
        return {
            "status": "success",
            "transcription": transcription
        }
    
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.post("/analyze_emotions", dependencies=[Depends(log_api_call)])
async def analyze_emotions(request: Request):
    """
    Analyzes text to determine emotions.
    Returns emotion scores from the emotion classification model.
    
    Accepts:
    - JSON with a "text" field 
    - Plain text
    - JSON with any field containing text (will use first string found)
    """
    try:
        # Get request content
        body = await request.body()
        text = ""
        
        # Try to parse as JSON first
        try:
            data = json.loads(body)
            # Check if it has a "text" field
            if isinstance(data, dict):
                if "text" in data:
                    text = data["text"]
                else:
                    # Look for any string field
                    for key, value in data.items():
                        if isinstance(value, str) and value:
                            text = value
                            break
            elif isinstance(data, str):
                text = data
        except json.JSONDecodeError:
            # If not JSON, treat as plain text
            text = body.decode("utf-8", errors="replace")
        
        # Ensure we have text to analyze
        if not text:
            return {"status": "error", "message": "No text provided"}
        
        # Process for emotions
        emotions = emotion_classifier(text)
        # Convert to dictionary format
        emotion_scores = {e["label"]: e["score"] for e in emotions[0]}
    
        # Update the global emotion scores
        global latest_emotion_scores
        latest_emotion_scores = emotion_scores
        
        return {
            "status": "success",
            "emotions": emotion_scores
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.post("/set_emotions", dependencies=[Depends(log_api_call)])
async def set_emotions(request: EmotionRequest):
    """Manually set emotion data"""
    try:
        global latest_emotion_scores
        if request.emotions:
            latest_emotion_scores = request.emotions
            return {"status": "success", "emotions": latest_emotion_scores}
        else:
            return {"status": "error", "message": "No emotions provided"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/get_emotion_data", dependencies=[Depends(log_api_call)])
async def get_emotion_data():
    """
    Return the latest emotion data for the ComfyUI custom node to consume.
    This endpoint is called by ComfyUI's custom nodes to get emotion data.
    """
    return {"emotions": latest_emotion_scores}

@app.post("/trigger_workflow", dependencies=[Depends(log_api_call)])
async def trigger_workflow(request: Request):
    """
    Trigger execution of the currently selected workflow in ComfyUI.
    This endpoint simply starts workflow execution - the ComfyUI nodes
    will fetch any required data (emotions, transformations) themselves.
    """
    try:
        # Try to parse JSON data if present
        try:
            data = await request.json()
            workflow_filename = data.get("workflow_filename")
            parameters = data.get("parameters", {})
        except:
            # If no JSON or empty request body, use defaults
            logger.info("No JSON body found, using first available workflow")
            workflow_filename = None
            parameters = {}
        
        # If no specific workflow requested, use the first available one
        if not workflow_filename:
            workflows = workflow_manager.get_available_workflows()
            if workflows["status"] != "success" or not workflows["workflows"]:
                return {"status": "error", "message": "No workflows available"}
            
            workflow_filename = workflows["workflows"][0]
            logger.info(f"Selected default workflow: {workflow_filename}")
        
        # Execute the workflow
        result = workflow_manager.execute_workflow(workflow_filename, parameters)
        
        return {
            "status": "success",
            "message": f"Workflow '{workflow_filename}' execution started",
            "details": result
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/execution_status", dependencies=[Depends(log_api_call)])
async def get_execution_status():
    """Get the current workflow execution status"""
    try:
        status = workflow_manager.get_execution_status()
        
        # Add transcription data if available
        transcription_file = os.path.join(cache_dir, "last_transcription.txt")
        
        if os.path.exists(transcription_file):
            with open(transcription_file, "r") as f:
                status["transcription"] = f.read().strip()
        
        return status
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/list_workflows", dependencies=[Depends(log_api_call)])
async def list_workflows():
    """List all available workflow files"""
    return workflow_manager.get_available_workflows()

@app.post("/upload_workflow", dependencies=[Depends(log_api_call)])
async def upload_workflow(file: UploadFile = File(...)):
    """
    Upload a workflow JSON file to the workflows directory
    """
    try:
        # Ensure workflows directory exists
        workflows_dir = os.path.join(os.path.dirname(__file__), "workflows")
        os.makedirs(workflows_dir, exist_ok=True)
        
        # Validate file
        if not file.filename.endswith('.json'):
            return {"status": "error", "message": "Only JSON files are allowed"}
        
        # Save file
        file_path = os.path.join(workflows_dir, file.filename)
        
        # Read file content
        file_content = await file.read()
        
        # Validate JSON
        try:
            json.loads(file_content)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON file"}
        
        # Write to file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return {
            "status": "success",
            "message": f"Workflow uploaded successfully as {file.filename}",
            "filename": file.filename
        }
    
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

#########################################
# 5. COMFYUI INTEGRATION ENDPOINTS
#########################################

@app.get("/proxy/comfyui/history", dependencies=[Depends(log_api_call)])
async def proxy_comfyui_history():
    """Proxy for ComfyUI history endpoint to avoid CORS issues"""
    try:
        comfyui_url = workflow_manager.test_comfyui_connection()
        response = requests.get(f"{comfyui_url}/history", timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/proxy/comfyui/view", dependencies=[Depends(log_api_call)])
async def proxy_comfyui_view(filename: str, type: str):
    """Proxy for ComfyUI image view endpoint to avoid CORS issues"""
    try:
        comfyui_url = workflow_manager.test_comfyui_connection()
        response = requests.get(f"{comfyui_url}/view?filename={filename}&type={type}", timeout=5)
        return Response(content=response.content, media_type=response.headers.get('content-type', 'image/png'))
    except Exception as e:
        return Response(content=b"Error loading image", media_type="text/plain", status_code=500)

@app.post("/analyze_transformation", dependencies=[Depends(log_api_call)])
async def analyze_transformation(request: Request):
    """
    Analyze the text to determine the most appropriate transformation.
    Uses LLM to select from the TRANSFORMATIONS list.
    """
    try:
        # Parse the JSON request
        data = await request.json()
        text = data.get("text", "")
        emotions = data.get("emotions", {})
        
        if not text:
            return {"status": "error", "message": "No text provided"}
        
        # Use LLM for transformation analysis
        if text_generator:
            try:
                # Construct a clear prompt for the LLM
                transformation_list = "\n".join([f"- From '{t['from']}' to '{t['to']}'" for t in TRANSFORMATIONS])
                prompt = f"""
                Based on the text below, select the most appropriate transformation from the list.
                Choose exactly one transformation that best matches what the person wants to change.
                
                Text: "{text}"
                
                Available transformations:
                {transformation_list}
                
                The most appropriate transformation is from:
                """
                
                # Generate response with LLM
                response = text_generator(prompt, max_length=len(prompt) + 150, do_sample=True)[0]['generated_text']
                
                # Extract the generated part
                generated = response[len(prompt):].strip()
                logger.info(f"Generated transformation text: {generated}")
                
                # Try to extract a valid transformation from the generated text
                transformation = None
                
                # Method 1: Look for exact phrases
                for t in TRANSFORMATIONS:
                    if f"'{t['from']}' to '{t['to']}'" in generated or f"{t['from']} to {t['to']}" in generated:
                        transformation = t
                        logger.info(f"Exact match found: {t}")
                        break
                
                # Method 2: Look for mentions of both the from and to states
                if not transformation:
                    for t in TRANSFORMATIONS:
                        from_term = t['from'].lower()
                        to_term = t['to'].lower()
                        if from_term in generated.lower() and to_term in generated.lower():
                            transformation = t
                            logger.info(f"Partial match found: {t}")
                            break
                
                # Method 3: Look for the closest match
                if not transformation:
                    for t in TRANSFORMATIONS:
                        from_term = t['from'].lower()
                        # Check if any word in the 'from' term appears in the generated text
                        for word in from_term.split():
                            if len(word) > 3 and word in generated.lower():
                                transformation = t
                                logger.info(f"Word match found: {word} in {t}")
                                break
                        if transformation:
                            break
                
                # If no transformation found through any method, use first in list
                if not transformation:
                    logger.warning(f"No transformation extracted, using first from list")
                    transformation = TRANSFORMATIONS[0]
                    
            except Exception as e:
                logger.error(f"Error in text generation: {e}")
                transformation = TRANSFORMATIONS[0]
        else:
            # No LLM available, use first transformation
            transformation = TRANSFORMATIONS[0]
        
        # Return the transformation
        return {
            "status": "success",
            "transformation": transformation,
            "text": text
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.post("/set_transformation", dependencies=[Depends(log_api_call)])
async def set_transformation(request: TransformationRequest):
    """Manually set the current transformation"""
    try:
        if request.transformation:
            # Save the transformation for reference
            with open(os.path.join(cache_dir, "current_transformation.json"), "w") as f:
                json.dump(request.transformation, f)
            
            return {"status": "success", "transformation": request.transformation}
        else:
            return {"status": "error", "message": "No transformation provided"}
        
        # Ensure required fields
        if "from" not in transformation or "to" not in transformation:
            return {"status": "error", "message": "Transformation must include 'from' and 'to' fields"}
        
        # Save transformation to file
        transformation_file = os.path.join(cache_dir, "current_transformation.json")
        with open(transformation_file, "w") as f:
            json.dump(transformation, f)
        
        return {
            "status": "success",
            "transformation": transformation
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/latest_transformation", dependencies=[Depends(log_api_call)])
async def get_latest_transformation():
    """Get the latest transformation"""
    transformation_file = os.path.join(cache_dir, "current_transformation.json")
    
    if os.path.exists(transformation_file):
        with open(transformation_file, "r") as f:
            transformation = json.load(f)
        return {"status": "success", "transformation": transformation}
    else:
        # Default transformation
        default = {"from": "Uncertainty", "to": "Clarity"}
        return {"status": "success", "transformation": default}

def extract_transformation_from_text(text):
    """Attempts to extract a valid transformation from generated text"""

@app.post("/upload_workflow", dependencies=[Depends(log_api_call)])
async def upload_workflow(file: UploadFile = File(...)):
    """
    Upload a workflow JSON file to the workflows directory
    """
    try:
        # Ensure workflows directory exists
        workflows_dir = os.path.join(os.path.dirname(__file__), "workflows")
        os.makedirs(workflows_dir, exist_ok=True)
        
        # Validate file
        if not file.filename.endswith('.json'):
            return {"status": "error", "message": "Only JSON files are allowed"}
        
        # Save file
        file_path = os.path.join(workflows_dir, file.filename)
        
        # Read file content
        file_content = await file.read()
        
        # Validate JSON
        try:
            json.loads(file_content)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON file"}
        
        # Write to file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return {
            "status": "success",
            "message": f"Workflow uploaded successfully as {file.filename}",
            "filename": file.filename
        }
    
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

#########################################
# 6. MEDIA ENDPOINTS
#########################################

@app.get("/list_media", dependencies=[Depends(log_api_call)])
async def list_media(type: str = None):
    """
    Lists all media files (videos and/or images)
    
    Parameters:
    - type: optional filter ("video", "image", or null for all)
    """
    try:
        output_dir = "/workspace/ComfyUI/output"
        media_files = []
        
        if not os.path.exists(output_dir):
            return {"status": "error", "message": "Output directory not found"}
        
        # Look for media files
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_type = None
                
                # Determine file type
                if file.endswith(('.mp4', '.webm', '.avi')):
                    file_type = "video"
                    url = f"/serve_media?path={file_path}&type=video"
                elif file.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    file_type = "image"
                    url = f"/serve_media?path={file_path}&type=image"
                
                # Apply type filter
                if file_type and (not type or file_type == type):
                    media_files.append({
                        "path": file_path,
                        "filename": file,
                        "type": file_type,
                        "url": url,
                        "modified_time": os.path.getmtime(file_path)
                    })
        
        # Sort by modification time (newest first)
        media_files.sort(key=lambda x: x["modified_time"], reverse=True)
        
        return {
            "status": "success",
            "media": media_files
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/serve_media", dependencies=[Depends(log_api_call)])
async def serve_media(path: str, type: str, download: bool = False):
    """
    Serves a media file by path
    
    Parameters:
    - path: file path
    - type: media type (video or image)
    - download: whether to force download
    """
    if not os.path.exists(path):
        return {"status": "error", "message": f"File not found: {path}"}
    
    # For security, verify the path is within the ComfyUI output directory
    comfyui_output = "/workspace/ComfyUI/output"
    if not path.startswith(comfyui_output):
        return {"status": "error", "message": "Invalid path"}
    
    # Set media type based on file extension
    media_type = None
    if type == "video":
        media_type = "video/mp4"
    elif type == "image":
        if path.endswith(".png"):
            media_type = "image/png"
        elif path.endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        elif path.endswith(".webp"):
            media_type = "image/webp"
    
    # Set download headers if requested
    headers = {}
    if download:
        filename = os.path.basename(path)
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    
    return FileResponse(path, media_type=media_type, headers=headers)

@app.get("/latest_media", dependencies=[Depends(log_api_call)])
async def get_latest_media(type: str = None):
    """
    Gets the latest generated media (video or image)
    
    Parameters:
    - type: optional filter ("video", "image", or null for all)
    """
    try:
        # Use workflow_manager's status first (for in-progress sessions)
        status = workflow_manager.get_execution_status()
        
        # Get the latest transcription if available
        transcription = None
        transcription_file = os.path.join(cache_dir, "last_transcription.txt")
        
        if os.path.exists(transcription_file):
            with open(transcription_file, "r") as f:
                transcription = f.read().strip()
        
        # Get latest transformation
        transformation = None
        transformation_file = os.path.join(cache_dir, "current_transformation.json")
        
        if os.path.exists(transformation_file):
            with open(transformation_file, "r") as f:
                transformation = json.load(f)
        
        # If workflow_manager has a media file and it matches the requested type
        if not type or type == "video":
            if status.get("last_video"):
                return {
                    "status": "success",
                    "type": "video",
                    "url": status["last_video"]["url"],
                    "filename": status["last_video"]["filename"],
                    "transcription": transcription,
                    "transformation": transformation,
                    "timestamp": time.time()
                }
        
        if not type or type == "image":
            if status.get("last_image"):
                return {
                    "status": "success", 
                    "type": "image",
                    "url": status["last_image"]["url"],
                    "transcription": transcription,
                    "transformation": transformation,
                    "timestamp": time.time()
                }
        
        # If nothing from workflow_manager, use the list_media endpoint
        media_list = await list_media(type)
        
        if media_list["status"] == "success" and media_list["media"]:
            latest = media_list["media"][0]
            return {
                "status": "success",
                "type": latest["type"],
                "url": latest["url"],
                "filename": latest["filename"],
                "transcription": transcription,
                "transformation": transformation,
                "timestamp": time.time()
            }
        
        # No media found
        return {
            "status": "waiting",
            "message": "No media available"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

#########################################
# 7. SYSTEM ENDPOINTS
#########################################

@app.get("/api_status", dependencies=[Depends(log_api_call)])
async def api_status():
    """Returns all registered API endpoints"""
    try:
        routes_info = []
        for route in app.routes:
            try:
                route_info = {
                    "path": str(route.path),
                    "name": str(route.name)
                }
                if hasattr(route, "methods"):
                    route_info["methods"] = [str(m) for m in route.methods]
                routes_info.append(route_info)
            except Exception as e:
                routes_info.append({"path": "Error getting route info", "error": str(e)})
        
        return {
            "status": "API is running",
            "route_count": len(routes_info),
            "routes": routes_info
        }
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return {"status": "error", "message": str(e), "traceback": error_traceback}

#########################################
# MAIN ENTRY POINT
#########################################

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)