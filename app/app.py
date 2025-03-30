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
import custom_manager
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import json
import time
from typing import Callable
import inspect
from functools import wraps
from pydantic import BaseModel

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

# Global variable to store the latest emotion scores
latest_emotion_scores = {}

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

# Add this global variable to store transformations
TRANSFORMATIONS = [
    {"transformation_from": "Closed off", "transformation_to": "Open"},
    {"transformation_from": "Stagnant", "transformation_to": "Creative"},
    {"transformation_from": "Fearful", "transformation_to": "Trusting"},
    {"transformation_from": "Hiding", "transformation_to": "Visible"},
    {"transformation_from": "Uncentered", "transformation_to": "Centered"},
    {"transformation_from": "Silenced", "transformation_to": "Honest"},
    {"transformation_from": "Disassociated", "transformation_to": "Embodied"},
    {"transformation_from": "Ruminating", "transformation_to": "Present"},
    {"transformation_from": "Hypervigilant", "transformation_to": "Relaxed"},
    {"transformation_from": "Illness", "transformation_to": "Health"},
    {"transformation_from": "Oppression", "transformation_to": "Freedom"},
    {"transformation_from": "Scarcity", "transformation_to": "Abundance"},
    {"transformation_from": "Controlling", "transformation_to": "Flexible"},
    {"transformation_from": "Codependent", "transformation_to": "Authentic Autonomy"},
    {"transformation_from": "Feeling Excluded", "transformation_to": "Belonging"},
    {"transformation_from": "Safety & Comfort", "transformation_to": "Embracing Transformation"},
    {"transformation_from": "Shame", "transformation_to": "Healthy Pride"},
    {"transformation_from": "External Validation", "transformation_to": "Wholeness"},
    {"transformation_from": "Controlling My Body", "transformation_to": "Listening to My Body"}
]

TRANSFORMATION_PROMPTS = {}
# Initialize a text-generation model for transformation analysis
try:
    # Use a smaller model for efficiency
    text_generator = pipeline("text-generation", 
                             model="distilgpt2", 
                             device=0 if torch.cuda.is_available() else -1)
except Exception as e:
    print(f"Warning: Could not load text generation model: {e}")
    text_generator = None

# Ensure the client directory exists
if not os.path.exists("client"):
    os.makedirs("client", exist_ok=True)
    print("Created client directory")

# Add at the top with other global variables
active_workflow = None

# Create a global variable to store the current workflow execution status
workflow_status = {
    "running": False,
    "client_id": None,
    "prompt_id": None,
    "progress": [],
    "current_node": None,
    "error": None,
    "start_time": None,
    "completed": False
}

class TransformationRequest(BaseModel):
    transformation: dict = None

@app.get("/", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def get_index():
    """Serve the projection experience as the main entry point."""
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
    """Serve the GUI dashboard."""
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(app_dir, "client", "gui.html")
        
        if os.path.exists(gui_path):
            with open(gui_path, "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content=f"<h1>Error: gui.html not found at {gui_path}</h1>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>")

@app.post("/transcribe_and_generate", dependencies=[Depends(log_api_call)])
async def transcribe_and_generate(file: UploadFile = File(...)):
    """Transcribe audio and generate a response"""
    global latest_emotion_scores
    
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
        
        # Process for emotions - using the existing emotion_classifier
        emotions = emotion_classifier(transcription)
        # Convert to dictionary format as in the original code
        emotion_scores = {e["label"]: e["score"] for e in emotions[0]}
        # Update the global emotion scores
        latest_emotion_scores = emotion_scores
        
        # Select a transformation using the original rule_based_transformation function
        transformation = rule_based_transformation(transcription, emotion_scores)
        
        # Save transformation to file for SphinxImportNode to read
        transformation_file = os.path.join(cache_dir, "current_transformation.json")
        with open(transformation_file, "w") as f:
            json.dump(transformation, f)
        
        # IMPORTANT: We're NOT triggering the workflow here anymore
        # Let the client handle that
        
        # Clean up
        os.unlink(temp_file.name)
        
        return {
            "status": "success",
            "transcription": transcription,
            "emotions": emotion_scores,
            "transformation": transformation
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.get("/get_emotion_data", dependencies=[Depends(log_api_call)])
async def get_emotion_data():
    """
    Return the latest emotion data for the ComfyUI custom node to consume.
    """
    return {"emotions": latest_emotion_scores}

@app.post("/trigger_workflow", dependencies=[Depends(log_api_call)])
async def trigger_workflow(request_data: TransformationRequest = None, request: Request = None):
    """Trigger a workflow execution with transformation data"""
    # Use a static flag to prevent multiple executions in a short time period
    global _last_workflow_trigger_time
    
    try:
        logger = logging.getLogger("api.trigger_workflow")

        logger.info(f"Request data: {request_data}")
        logger.info(f"Request headers: {request.headers}")
        
        # Add rate limiting to prevent multiple executions
        current_time = time.time()
        if hasattr(trigger_workflow, '_last_execution_time') and current_time - trigger_workflow._last_execution_time < 10.0:
            logger.info("Ignoring duplicate workflow trigger (rate limited)")
            return {"status": "ignored", "message": "Duplicate request ignored (rate limited)"}
        
        # Set last execution time
        trigger_workflow._last_execution_time = current_time

        # Extract transformation from the request
        transformation = None
        if request_data and request_data.transformation:
            transformation = request_data.transformation
            logger.info(f"Received transformation data from JSON body: {transformation}")
        
        # If no transformation was provided in JSON, try to read from raw request
        if not transformation and request:
            try:
                # Read the raw body
                body = await request.body()
                logger.debug(f"Raw request body: {body}")
                logger.debug(f"Content-Type: {request.headers.get('content-type')}")
                
                # Parse the body as JSON if it's not empty
                if body:
                    try:
                        data = json.loads(body)
                        logger.debug(f"Parsed JSON data: {data}")  # Log the full parsed data structure
                        
                        # Check for transformation in different possible structures
                        if isinstance(data, dict):
                            if 'transformation' in data:
                                transformation = data['transformation']
                                logger.info(f"Found transformation in first level: {transformation}")
                            elif 'transformation_from' in data and 'transformation_to' in data:
                                transformation = data
                                logger.info(f"Found direct transformation fields: {transformation}")
                    except json.JSONDecodeError as json_err:
                        logger.error(f"JSON parse error: {json_err}")
                        logger.debug(f"Request body content: {body.decode('utf-8', errors='replace')}")
            except Exception as e:
                logger.error(f"Error processing request: {e}")
        
        # If no transformation was provided, use a default
        if not transformation:
            transformation = {
                "transformation_from": "Fearful", 
                "transformation_to": "Trusting"
            }
            logger.info("Using default transformation")
        else:
            logger.info(f"Using provided transformation: {transformation}")
            
        # Use the correct workflow file
        workflow_file = "lumalabs.json"
        
        # Execute using custom_manager
        logger.info(f"Executing workflow {workflow_file} with transformation {transformation}")
        result = custom_manager.execute_workflow(workflow_file, transformation)
        
        # Save the current transformation for reference
        cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        transformation_file = os.path.join(cache_dir, "current_transformation.json")
        
        with open(transformation_file, "w") as f:
            json.dump(transformation, f)
        
        return {"status": "success", "message": "Workflow triggered", "details": result}
    
    except Exception as e:
        import traceback
        logger.error(f"Error in trigger_workflow: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.get("/client/script.js", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def get_script_js():
    """Serve the script.js file."""
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

# Static file serving with absolute path
app_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(app_dir, "client")
app.mount("/client", StaticFiles(directory=client_dir), name="client")

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
async def analyze_transformation(request: dict):
    """
    Analyze the text to determine the most appropriate transformation.
    """
    text = request.get("text", "")
    emotions = request.get("emotions", {})
    
    if not text:
        return {"error": "No text provided for analysis"}
    
    # If we have a text generator, use it
    if text_generator:
        # Construct a prompt for the LLM
        prompt = f"""
        Based on the following text and emotions, identify which transformation is most appropriate.
        
        Text: "{text}"
        
        Emotions: {json.dumps(emotions)}
        
        Possible transformations:
        {json.dumps(TRANSFORMATIONS)}
        
        The most appropriate transformation is:
        """
        
        # Generate response (simple approach)
        try:
            response = text_generator(prompt, max_length=len(prompt) + 50, do_sample=True)[0]['generated_text']
            # Extract the generated part
            generated = response[len(prompt):].strip()
            
            # Fallback to rule-based method if generation isn't helpful
            if not generated:
                transformation = rule_based_transformation(text, emotions)
            else:
                # Try to extract a valid transformation from the generated text
                transformation = extract_transformation(generated)
                if not transformation:
                    transformation = rule_based_transformation(text, emotions)
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            transformation = rule_based_transformation(text, emotions)
    else:
        # Fallback to rule-based method
        transformation = rule_based_transformation(text, emotions)
    
    # Return the transformation
    return {"transformation": transformation}

def rule_based_transformation(text, emotions):
    """Simple rule-based approach to select a transformation"""
    text = text.lower()
    
    # Get the top emotion
    top_emotion = None
    top_score = 0
    for emotion, score in emotions.items():
        if score > top_score:
            top_emotion = emotion
            top_score = score
    
    # Map emotions and keywords to transformations
    if "fear" in text or "scared" in text or "afraid" in text or top_emotion == "fear":
        return TRANSFORMATIONS[2]  # Fearful -> Trusting
    elif "alone" in text or "lonely" in text or top_emotion == "lonely":
        return TRANSFORMATIONS[14]  # Feeling Excluded -> Belonging
    elif "stuck" in text or "cant move" in text or "frozen" in text:
        return TRANSFORMATIONS[1]  # Stagnant -> Creative
    elif "hide" in text or "hiding" in text or "invisible" in text:
        return TRANSFORMATIONS[3]  # Hiding -> Visible
    elif "shame" in text or "embarrassed" in text or top_emotion == "shame":
        return TRANSFORMATIONS[16]  # Shame -> Healthy Pride
    elif "control" in text or "perfect" in text:
        return TRANSFORMATIONS[12]  # Controlling -> Flexible
    elif "worry" in text or "anxious" in text or top_emotion == "anxiety":
        return TRANSFORMATIONS[7]  # Ruminating -> Present
    elif "validation" in text or "approval" in text:
        return TRANSFORMATIONS[17]  # External Validation -> Wholeness
    elif "body" in text or "health" in text or "sick" in text:
        return TRANSFORMATIONS[18]  # Controlling My Body -> Listening to My Body
    elif "not enough" in text or "lack" in text:
        return TRANSFORMATIONS[11]  # Scarcity -> Abundance
    
    # Default to a random transformation if no match
    import random
    return random.choice(TRANSFORMATIONS)

def extract_transformation(text):
    """Try to extract a valid transformation from generated text"""
    for t in TRANSFORMATIONS:
        if f"{t['from']} to {t['to']}" in text:
            return t
        if t['from'].lower() in text.lower() and t['to'].lower() in text.lower():
            return t
    return None

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

@app.post("/trigger_video_transformation", dependencies=[Depends(log_api_call)])
async def trigger_video_transformation(request: dict):
    """
    Trigger the ComfyUI workflow to generate a transformation video.
    """
    try:
        transformation = request.get("transformation", None)
        if not transformation:
            return {"status": "error", "message": "No transformation provided"}
        
        from_state = transformation.get("from", "uncertainty")
        to_state = transformation.get("to", "confidence")
        
        # Get workflow filename if provided
        workflow_filename = transformation.get("workflow_filename", None)
        
        # Import the script
        import run_video_workflow
        
        # Run the workflow in a background thread to not block the API
        import threading
        thread = threading.Thread(
            target=run_video_workflow.run_video_transformation,
            args=(from_state, to_state, workflow_filename)
        )
        thread.daemon = True
        thread.start()
        
        return {
            "status": "success", 
            "message": "Video transformation workflow triggered successfully",
            "transformation": {
                "from": from_state,
                "to": to_state,
                "workflow": workflow_filename or "default"
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/list_workflows", dependencies=[Depends(log_api_call)])
async def list_workflows():
    """List all available workflow files"""
    return custom_manager.get_available_workflows()

@app.post("/execute_workflow", dependencies=[Depends(log_api_call)])
async def execute_workflow(request: Request):
    """Execute a workflow file with optional parameters"""
    try:
        data = await request.json()
        workflow_filename = data.get("workflow_filename")
        parameters = data.get("parameters", {})
        
        if not workflow_filename:
            return {"status": "error", "message": "Missing workflow_filename parameter"}
        
        result = custom_manager.execute_workflow(workflow_filename, parameters)
        return result
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/execution_status", dependencies=[Depends(log_api_call)])
async def get_execution_status():
    """Get the current workflow execution status"""
    try:
        status = custom_manager.get_execution_status()
        
        # Add transcription data if available
        cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        transcription_file = os.path.join(cache_dir, "last_transcription.txt")
        
        if os.path.exists(transcription_file):
            with open(transcription_file, "r") as f:
                status["transcription"] = f.read().strip()
        
        return status
    except Exception as e:
        return {"error": str(e)}

@app.get("/workflows", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def serve_workflows_page():
    """Serve the workflows page"""
    return get_html_content("client/workflows.html")

@app.get("/workflow_tester", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def serve_workflow_tester():
    """Serve the workflow tester page"""
    try:
        # Use direct file loading like the working endpoints
        app_dir = os.path.dirname(os.path.abspath(__file__))
        tester_path = os.path.join(app_dir, "client", "workflow_tester.html")
        
        if os.path.exists(tester_path):
            with open(tester_path, "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content=f"<h1>Error: workflow_tester.html not found at {tester_path}</h1>")
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return HTMLResponse(content=f"""
        <html>
            <head><title>Error</title></head>
            <body>
                <h1>Error serving workflow_tester.html</h1>
                <p>{str(e)}</p>
                <pre>{error_traceback}</pre>
            </body>
        </html>
        """)

@app.get("/api_status", dependencies=[Depends(log_api_call)])
async def api_status():
    """Return a list of all registered API endpoints for debugging"""
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

@app.get("/debug_logs", dependencies=[Depends(log_api_call)])
async def get_debug_logs():
    """Get the debug logs"""
    try:
        debug_dir = os.path.join(os.path.dirname(__file__), "debug")
        log_file = os.path.join(debug_dir, "workflow_debug.log")
        
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = f.read()
            return {"status": "success", "logs": logs}
        else:
            return {"status": "error", "message": "No debug logs found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test_comfyui", dependencies=[Depends(log_api_call)])
async def test_comfyui():
    """Test the ComfyUI connection"""
    try:
        import comfyui_test
        result = comfyui_test.test_comfyui_connection()
        
        if result:
            return {"status": "success", "message": f"ComfyUI is accessible at {result}"}
        else:
            return {"status": "error", "message": "Could not connect to ComfyUI"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/workflow_status", dependencies=[Depends(log_api_call)])
async def get_workflow_status():
    """Get the current status of the running workflow"""
    global workflow_status
    
    # Calculate elapsed time if workflow is running
    if workflow_status["running"] and workflow_status["start_time"]:
        elapsed = time.time() - workflow_status["start_time"]
        workflow_status["elapsed_seconds"] = round(elapsed, 1)
        
    return workflow_status

@app.get("/latest_video", dependencies=[Depends(log_api_call)])
async def get_latest_video():
    """Get the latest video file generated by ComfyUI"""
    try:
        # Get ComfyUI URL to determine its location
        import run_video_workflow
        comfyui_url = run_video_workflow.test_comfyui_connection()
        
        # Determine ComfyUI output directory path
        # ComfyUI typically saves outputs to its 'output' directory
        comfyui_dir = "/workspace/ComfyUI"  # Base ComfyUI directory
        output_dir = os.path.join(comfyui_dir, "output")
        
        if not os.path.exists(output_dir):
            return {"status": "error", "message": "ComfyUI output directory not found"}
        
        # Find all mp4 files
        video_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.mp4'):
                    file_path = os.path.join(root, file)
                    video_files.append({
                        "path": file_path,
                        "filename": file,
                        "modified_time": os.path.getmtime(file_path)
                    })
        
        if not video_files:
            return {"status": "error", "message": "No video files found"}
            
        # Sort by modification time (newest first)
        video_files.sort(key=lambda x: x["modified_time"], reverse=True)
        latest_video = video_files[0]
        
        # Create a URL to serve the file
        video_url = f"/serve_video?path={latest_video['path']}"
        
        return {
            "status": "success",
            "video_url": video_url,
            "filename": latest_video["filename"],
            "modified": latest_video["modified_time"]
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.get("/serve_video", dependencies=[Depends(log_api_call)])
async def serve_video(path: str, download: bool = False):
    """Serve a video file from the ComfyUI output directory"""
    if not os.path.exists(path):
        return {"status": "error", "message": f"Video not found: {path}"}
    
    # For security, verify the path is within the ComfyUI output directory
    comfyui_output = "/workspace/ComfyUI/output"
    if not path.startswith(comfyui_output):
        return {"status": "error", "message": "Invalid path"}
    
    # Set up the response with the appropriate headers
    headers = {}
    if download:
        filename = os.path.basename(path)
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    
    return FileResponse(path, media_type="video/mp4", headers=headers)

@app.get("/latest_transformation", dependencies=[Depends(log_api_call)])
async def get_latest_transformation():
    """Retrieve the latest transformation that was applied"""
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    transformation_file = os.path.join(cache_dir, "current_transformation.json")
    
    if os.path.exists(transformation_file):
        with open(transformation_file, "r") as f:
            transformation = json.load(f)
        return {"status": "success", "transformation": transformation}
    else:
        raise HTTPException(status_code=404, detail="No transformation found")

@app.get("/custom_gui", response_class=HTMLResponse, dependencies=[Depends(log_api_call)])
async def serve_custom_gui():
    """Serve the custom GUI page"""
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(app_dir, "client", "custom_gui.html")
        
        if os.path.exists(gui_path):
            with open(gui_path, "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        else:
            return HTMLResponse(content=f"<h1>Error: custom_gui.html not found</h1>")
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1><pre>{error_traceback}</pre>")

@app.get("/download_video", dependencies=[Depends(log_api_call)])
async def download_video(filename: str):
    """Download a video by filename from the ComfyUI output directory"""
    # Search for the file in the output directory
    comfyui_output = "/workspace/ComfyUI/output"
    
    # Search recursively for the file
    for root, dirs, files in os.walk(comfyui_output):
        if filename in files:
            file_path = os.path.join(root, filename)
            return FileResponse(
                file_path, 
                media_type="video/mp4",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )
    
    return {"status": "error", "message": f"Video not found: {filename}"}

@app.get("/list_videos", dependencies=[Depends(log_api_call)])
async def list_videos():
    """List all video files in the ComfyUI output directory"""
    try:
        output_dir = "/workspace/ComfyUI/output"
        video_files = []
        
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.mp4'):
                    file_path = os.path.join(root, file)
                    video_files.append({
                        "path": file_path,
                        "filename": file,
                        "url": f"/download_video?filename={file}",
                        "modified_time": os.path.getmtime(file_path)
                    })
        
        # Sort by modification time (newest first)
        video_files.sort(key=lambda x: x["modified_time"], reverse=True)
        
        return {"status": "success", "videos": video_files}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/latest_media", dependencies=[Depends(log_api_call)])
async def get_latest_media():
    """Get the latest generated media (video or image)"""
    try:
        # Get the status from custom_manager
        status = custom_manager.get_execution_status()
        
        # Get the latest transcription if available
        transcription = None
        cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        transcription_file = os.path.join(cache_dir, "last_transcription.txt")
        
        if os.path.exists(transcription_file):
            with open(transcription_file, "r") as f:
                transcription = f.read().strip()
        
        # Check for video first (prioritize video over image)
        if status.get("last_video"):
            return {
                "status": "success",
                "type": "video",
                "url": status["last_video"]["url"],
                "filename": status["last_video"]["filename"],
                "transcription": transcription,
                "timestamp": time.time()
            }
        # Fall back to image if no video
        elif status.get("last_image"):
            return {
                "status": "success", 
                "type": "image",
                "url": status["last_image"]["url"],
                "transcription": transcription,
                "timestamp": time.time()
            }
        else:
            return {
                "status": "waiting",
                "message": "No media available yet"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)