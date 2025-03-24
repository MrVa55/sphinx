import whisper
import tempfile
import os
from fastapi import FastAPI, File, UploadFile
from transformers import pipeline
from diffusers import StableDiffusionPipeline
import torch
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
import requests
import sys
sys.path.append('/workspace/app')
import workflow_manager
import glob
from fastapi.responses import FileResponse, HTMLResponse
import uuid
import time

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]  # Add this line
)

# Set cache directories to avoid re-downloading models
os.environ["TRANSFORMERS_CACHE"] = "/root/.cache/huggingface"
os.environ["HF_HOME"] = "/root/.cache/huggingface"

# Global variable to store the latest emotion scores.
# This will be updated every time transcribe_and_generate is called.
latest_emotion_scores = {}

# Load models
whisper_model = whisper.load_model("base")
emotion_classifier = pipeline(
    "text-classification", 
    model="joeddav/distilbert-base-uncased-go-emotions-student", 
    top_k=None,
    device=0  # Use GPU explicitly
)
sd_pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5").to("cuda")

def generate_prompt(emotions):
    """
    Converts emotion scores into a Stable Diffusion prompt.
    """
    emotion_descriptions = {
        "joy": "a vibrant, colorful, sunny landscape full of life and happiness",
        "sadness": "a dark, rainy, moody environment filled with sorrow",
        "anger": "a fiery, chaotic scene with red tones and intense energy",
        "fear": "a dark forest with eerie shadows and a sense of mystery",
        "surprise": "a surreal dreamlike world with unexpected shapes and colors",
        "love": "a warm, romantic sunset with soft glowing light"
    }
    
    # Sort emotions by confidence and build a blended prompt.
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    prompt = ", ".join(
        [f"{emotion_descriptions[e[0]]} ({e[1]:.2f})" for e in sorted_emotions if e[0] in emotion_descriptions]
    )
    return prompt if prompt else "a neutral scene with balanced colors"

@app.post("/transcribe_and_generate")
async def transcribe_and_generate(file: UploadFile = File(...)):
    """
    Transcribes an audio file, detects emotions, and generates an image based on detected emotions.
    Updates the global latest_emotion_scores.
    """
    global latest_emotion_scores

    # Save the uploaded audio file temporarily.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp_filename = tmp.name
        content = await file.read()
        tmp.write(content)
    
    # Transcribe using Whisper.
    result = whisper_model.transcribe(tmp_filename)
    text = result["text"]
    
    # Delete the temporary file.
    os.remove(tmp_filename)
    
    # Run emotion classification on the transcription.
    emotions = emotion_classifier(text)
    # Assume emotions[0] is a list of dictionaries, each with keys "label" and "score".
    emotion_results = {e["label"]: e["score"] for e in emotions[0]}
    
    # Generate a Stable Diffusion prompt.
    prompt = generate_prompt(emotion_results)
    
    # Generate an image using Stable Diffusion.
    image = sd_pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]
    
    # Save the generated image to disk.
    output_filename = "output.png"
    image.save(output_filename)
    
    # Update the global emotion scores.
    latest_emotion_scores = emotion_results
    
    # MINIMAL CHANGE: Silently trigger the workflow without affecting other functionality
    try:
        # Use existing endpoint without logging
        requests.post("http://127.0.0.1:8010/trigger_workflow", timeout=0.1)
    except:
        # Intentionally ignore any errors to not break existing functionality
        pass
    
    return {
        "transcription": text,
        "emotions": emotion_results,
        "prompt": prompt,
        "image": output_filename
    }

@app.get("/get_emotion_data")
async def get_emotion_data():
    """
    Returns the latest emotion scores as a JSON object with an 'emotions' key.
    This endpoint is called by the EmotionImportNode in ComfyUI.
    """
    return {"emotions": latest_emotion_scores}

@app.post("/trigger_workflow")
async def api_trigger_workflow():
    """Triggers the ComfyUI workflow using your custom emotion nodes."""
    try:
        print("Triggering workflow with custom emotion nodes...")
        
        # Find the best ComfyUI URL
        comfyui_url = workflow_manager.test_comfyui_connection()
        print(f"Using ComfyUI URL: {comfyui_url}")
        
        thread = workflow_manager.run_workflow_with_custom_nodes(comfyui_url)
        
        return {
            "status": "success", 
            "message": "Custom emotion workflow triggered",
            "client_id": "sphinx_api_client"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/latest_image")
async def get_latest_image():
    """Returns the most recently generated image from ComfyUI output directory."""
    try:
        # Look for emotion images first
        output_dir = "/ComfyUI/output"
        pattern = os.path.join(output_dir, "ComfyUI_emotion*.png")
        image_files = glob.glob(pattern)
        
        if not image_files:
            # Try any image if no emotion ones found
            pattern = os.path.join(output_dir, "*.png")
            image_files = glob.glob(pattern)
        
        if not image_files:
            return {"status": "error", "message": "No generated images found"}
        
        # Sort by modification time (newest first)
        latest_image = max(image_files, key=os.path.getmtime)
        
        # Return the image file
        return FileResponse(latest_image, media_type="image/png")
        
    except Exception as e:
        print(f"Error retrieving latest image: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/view_results", response_class=HTMLResponse)
async def view_results():
    """Shows a simple page that displays the latest generated images."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ComfyUI Results Viewer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .image-container { margin-top: 20px; }
            img { max-width: 100%; height: auto; border: 1px solid #ddd; }
            .refresh-button { margin-top: 20px; padding: 10px 15px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            .status { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>ComfyUI Generated Images</h1>
        <p>The latest image generated from your emotion-based workflow:</p>
        
        <div class="image-container">
            <img id="latest-image" src="/latest_image" alt="Latest generated image">
        </div>
        
        <button class="refresh-button" onclick="refreshImage()">Refresh Image</button>
        <div class="status" id="status-message"></div>
        
        <script>
            function refreshImage() {
                document.getElementById('status-message').textContent = 'Refreshing...';
                
                // Add a timestamp to prevent caching
                const timestamp = new Date().getTime();
                const imgElement = document.getElementById('latest-image');
                imgElement.src = '/latest_image?' + timestamp;
                
                imgElement.onload = function() {
                    document.getElementById('status-message').textContent = 'Image refreshed!';
                };
                
                imgElement.onerror = function() {
                    document.getElementById('status-message').textContent = 'Error loading image. Try again in a moment.';
                };
            }
            
            // Auto-refresh every 10 seconds
            setInterval(refreshImage, 10000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/client")
async def client_redirect():
    """Redirects to the client HTML page for viewing streaming results."""
    # The client.html is likely in the ComfyUI web directory or custom_nodes directory
    client_locations = [
        "/ComfyUI/web/client.html", 
        "/ComfyUI/custom_nodes/client.html",
        "/workspace/client/client.html",
        "/client/client.html"
    ]
    
    # Find the client.html file
    client_path = None
    for path in client_locations:
        if os.path.exists(path):
            client_path = path
            break
    
    if not client_path:
        return {"status": "error", "message": "Client HTML file not found"}
    
    # Create a response that redirects to the client file
    return FileResponse(client_path)

@app.get("/client_viewer", response_class=HTMLResponse)
async def client_viewer():
    """
    Serves a modified client.html that connects to the right WebSocket endpoint
    with the most recent client ID.
    """
    # Find the client.html file
    client_locations = [
        "/workspace/client/client.html",
        "/client/client.html",
        "/ComfyUI/web/client.html",
        "/ComfyUI/custom_nodes/client.html"
    ]
    
    client_html = None
    for path in client_locations:
        if os.path.exists(path):
            with open(path, "r") as f:
                client_html = f.read()
            print(f"Found client.html at: {path}")
            break
    
    if not client_html:
        return "Client HTML file not found"
    
    # Get the most recent prompt info if available
    client_id = str(uuid.uuid4())  # Default
    prompt_id = ""
    try:
        if os.path.exists("/workspace/app/last_prompt.json"):
            with open("/workspace/app/last_prompt.json", "r") as f:
                prompt_info = json.load(f)
                client_id = prompt_info.get("client_id", client_id)
                prompt_id = prompt_info.get("prompt_id", "")
                timestamp = prompt_info.get("timestamp", 0)
                
                # Only use if it's less than 5 minutes old
                if time.time() - timestamp > 300:
                    client_id = str(uuid.uuid4())
                    prompt_id = ""
    except Exception as e:
        print(f"Error reading last prompt info: {e}")
    
    # Create a script element to inject into the HTML
    ws_script = f"""
    <script>
        // Automatically use the right WebSocket URL and client ID
        const serverAddress = "dlz1l9gphefry5-3020.proxy.runpod.net";
        const clientId = "{client_id}";
        const lastPromptId = "{prompt_id}";
        
        // This will be executed when the page loads
        document.addEventListener('DOMContentLoaded', function() {{
            console.log("Using WebSocket:", `wss://${{serverAddress}}/ws?clientId=${{clientId}}`);
            
            // If this information exists in the page, update it
            if (document.getElementById('client-id')) {{
                document.getElementById('client-id').textContent = clientId;
            }}
            
            if (document.getElementById('prompt-id') && lastPromptId) {{
                document.getElementById('prompt-id').textContent = lastPromptId;
            }}
            
            // You can add other initialization code here
        }});
    </script>
    """
    
    # Replace the WebSocket connection in the client.html
    # (This assumes the client.html has some kind of WebSocket setup we can modify)
    modified_html = client_html
    
    # Insert our custom script at the end of the head section
    if "<head>" in modified_html:
        modified_html = modified_html.replace("</head>", f"{ws_script}\n</head>")
    else:
        # If no head section, add it at the top of the body or the start of the document
        if "<body>" in modified_html:
            modified_html = modified_html.replace("<body>", f"<body>\n{ws_script}")
        else:
            modified_html = f"{ws_script}\n{modified_html}"
    
    return modified_html

@app.get("/streaming_client", response_class=HTMLResponse)
async def streaming_client():
    """
    Creates a streaming client that connects directly to ComfyUI WebSocket.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Welcome to the turning point</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    #imageContainer { margin-top: 20px; }
    img { max-width: 100%; border: 1px solid #ccc; }
    #emotionsContainer {
      margin: 20px 0;
      padding: 10px;
      background-color: #f5f5f5;
      border-radius: 5px;
    }
    #audioControls, #frameControls, #workflowControls {
      margin: 20px 0;
      padding: 10px;
      background-color: #e0e0e0;
      border-radius: 5px;
    }
    button {
      padding: 10px 20px;
      margin: 5px;
      border-radius: 5px;
      cursor: pointer;
    }
    .recording { 
      background-color: #ff4444;
      color: white;
    }
    #thumbnails {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 10px;
      max-height: 200px;
      overflow-y: auto;
    }
    .thumbnail {
      width: 80px;
      height: 80px;
      object-fit: cover;
      border: 1px solid #ddd;
      cursor: pointer;
    }
    .thumbnail.selected {
      border: 3px solid #4CAF50;
    }
    .status-bar {
      background-color: #f8f8f8;
      padding: 5px 10px;
      border-radius: 3px;
      margin: 5px 0;
      font-family: monospace;
    }
  </style>
</head>
<body>
  <h1>Welcome to the turning point</h1>
  <p>Connection Status: <span id="status">Connecting...</span></p>
  
  <div id="serverConfig" style="margin: 20px 0;">
    <div>
        <label for="apiServer">API Server (port 8010):</label>
        <input type="text" id="apiServer" style="width: 300px; padding: 5px;" 
               value="https://dlz1l9gphefry5-8010.proxy.runpod.net">
    </div>
    <div style="margin-top: 10px;">
        <label for="wsServer">WebSocket Server (port 3020):</label>
        <input type="text" id="wsServer" style="width: 300px; padding: 5px;" 
               value="dlz1l9gphefry5-3020.proxy.runpod.net">
    </div>
    <button onclick="updateServers()">Update Servers</button>
  </div>

  <div id="audioControls">
    <button id="recordButton">Start Recording</button>
    <span id="recordingStatus"></span>
  </div>
  
  <div id="workflowControls">
    <h3>Workflow Control:</h3>
    <button id="triggerWorkflowBtn">Trigger Workflow</button>
    <div id="workflowStatus" class="status-bar">Ready</div>
    <div id="executionInfo" class="status-bar">No active execution</div>
  </div>
  
  <div id="frameControls">
    <h3>Frame Recording:</h3>
    <button id="startFrameRecording">Start Recording Frames</button>
    <button id="saveFrames" disabled>Save Frames</button>
    <button id="clearFrames" disabled>Clear Frames</button>
    <span id="frameStatus">Not recording frames</span>
  </div>

  <div id="emotionsContainer">
    <h3>Detected Emotions:</h3>
    <div id="emotionsDisplay">Waiting for emotions data...</div>
  </div>
  
  <div id="imageContainer">
    <img id="streamedImage" src="" alt="Streamed Image">
  </div>
  
  <div id="thumbnails"></div>

  <script>
    // Server configuration
    let apiServerUrl = localStorage.getItem('apiServerUrl') || 'https://dlz1l9gphefry5-8010.proxy.runpod.net';
    let wsServerUrl = localStorage.getItem('wsServerUrl') || 'dlz1l9gphefry5-3020.proxy.runpod.net';
    
    // Fixed client ID that matches what we use in workflow_manager.py
    const clientId = "sphinx_api_client";
    
    // Connect to both the ComfyUI WebSocket and our custom Sphinx WebSocket
    const wsComfyUrl = `wss://${wsServerUrl}/ws?clientId=${clientId}`;
    const wsSphinxUrl = `wss://${wsServerUrl}/ws_sphinx`;
    
    // UI elements
    const statusEl = document.getElementById("status");
    const imgEl = document.getElementById("streamedImage");
    const emotionsEl = document.getElementById("emotionsDisplay");
    const recordButton = document.getElementById("recordButton");
    const recordingStatus = document.getElementById("recordingStatus");
    const startFrameRecordingBtn = document.getElementById("startFrameRecording");
    const saveFramesBtn = document.getElementById("saveFrames");
    const clearFramesBtn = document.getElementById("clearFrames");
    const frameStatusEl = document.getElementById("frameStatus");
    const thumbnailsEl = document.getElementById("thumbnails");
    const triggerWorkflowBtn = document.getElementById("triggerWorkflowBtn");
    const workflowStatus = document.getElementById("workflowStatus");
    const executionInfo = document.getElementById("executionInfo");
    
    // Recording state
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    
    // Frame recording variables
    let isRecordingFrames = false;
    let recordedFrames = [];
    let selectedFrameIndex = -1;
    
    // Audio recording setup - exactly as in your original client
    async function setupAudioRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          console.log('Audio recorded, size:', audioBlob.size, 'bytes');
          await sendAudioToServer(audioBlob);
          audioChunks = [];
        };
        
        recordButton.addEventListener('click', toggleRecording);
        console.log("Audio recording setup complete");
      } catch (err) {
        console.error('Error accessing microphone:', err);
        recordingStatus.textContent = 'Error: Could not access microphone';
      }
    }
    
    function toggleRecording() {
      if (!isRecording) {
        mediaRecorder.start();
        recordButton.textContent = 'Stop Recording';
        recordButton.classList.add('recording');
        recordingStatus.textContent = 'Recording...';
        isRecording = true;
      } else {
        mediaRecorder.stop();
        recordButton.textContent = 'Start Recording';
        recordButton.classList.remove('recording');
        recordingStatus.textContent = 'Processing audio...';
        isRecording = false;
      }
    }
    
    async function sendAudioToServer(audioBlob) {
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.wav');
      
      try {
        const response = await fetch(`${apiServerUrl}/transcribe_and_generate`, {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('Server response:', data);
          recordingStatus.textContent = 'Audio processed successfully!';
        } else {
          console.error('Server error:', response.status);
          recordingStatus.textContent = `Error: Server returned ${response.status}`;
        }
      } catch (error) {
        console.log('Fetch completed (ignore CORS warning)');
        recordingStatus.textContent = 'Audio sent for processing...';
      }
    }
    
    // Frame recording functions
    function toggleFrameRecording() {
      if (isRecordingFrames) {
        // Stop recording
        isRecordingFrames = false;
        startFrameRecordingBtn.textContent = "Start Recording Frames";
        startFrameRecordingBtn.classList.remove('recording');
        frameStatusEl.textContent = `Recording stopped (${recordedFrames.length} frames captured)`;
      } else {
        // Start recording
        isRecordingFrames = true;
        recordedFrames = [];
        selectedFrameIndex = -1;
        thumbnailsEl.innerHTML = '';
        startFrameRecordingBtn.textContent = "Stop Recording Frames";
        startFrameRecordingBtn.classList.add('recording');
        frameStatusEl.textContent = "Recording frames...";
        saveFramesBtn.disabled = true;
        clearFramesBtn.disabled = true;
      }
    }
    
    function saveFrameFromImageElement() {
      if (!imgEl.complete || !imgEl.src) {
        console.warn('Image not loaded, cannot capture frame');
        return;
      }
      
      // Create a canvas to capture the image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = imgEl.naturalWidth;
      canvas.height = imgEl.naturalHeight;
      ctx.drawImage(imgEl, 0, 0);
      
      // Convert to blob
      canvas.toBlob(blob => {
        const frameUrl = URL.createObjectURL(blob);
        recordedFrames.push({
          blob: blob,
          url: frameUrl
        });
        
        // Enable buttons if we have frames
        if (recordedFrames.length > 0) {
          saveFramesBtn.disabled = false;
          clearFramesBtn.disabled = false;
        }
        
        // Create thumbnail
        const thumbnail = document.createElement('img');
        thumbnail.src = frameUrl;
        thumbnail.className = 'thumbnail';
        thumbnail.addEventListener('click', () => {
          // Select this thumbnail
          document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('selected'));
          thumbnail.classList.add('selected');
          selectedFrameIndex = recordedFrames.length - 1;
          
          // Show this frame
          imgEl.src = frameUrl;
        });
        
        thumbnailsEl.appendChild(thumbnail);
        frameStatusEl.textContent = `Captured frame #${recordedFrames.length}`;
      }, 'image/png');
    }
    
    function saveFrames() {
      if (recordedFrames.length === 0) return;
      
      // Create a JSZip instance
      const zip = new JSZip();
      const folder = zip.folder("frames");
      
      // Add each frame to the zip
      recordedFrames.forEach((frame, index) => {
        const filename = `frame_${index.toString().padStart(5, '0')}.png`;
        folder.file(filename, frame.blob);
      });
      
      // Generate the zip and trigger download
      zip.generateAsync({type: "blob"}).then((content) => {
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(content);
        downloadLink.download = `frames_${new Date().toISOString().replace(/:/g, '-')}.zip`;
        downloadLink.click();
        
        frameStatusEl.textContent = `Saved ${recordedFrames.length} frames to zip file`;
      });
    }
    
    function clearFrames() {
      recordedFrames = [];
      selectedFrameIndex = -1;
      thumbnailsEl.innerHTML = '';
      saveFramesBtn.disabled = true;
      clearFramesBtn.disabled = true;
      frameStatusEl.textContent = 'Cleared all frames';
    }
    
    // WebSocket handling for ComfyUI direct connection
    let wsComfy = null;
    
    function connectToComfyWebSocket() {
      wsComfy = new WebSocket(wsComfyUrl);
      wsComfy.binaryType = "blob"; // ComfyUI sends binary image data
      
      wsComfy.onopen = function() {
        console.log("Connected to ComfyUI WebSocket:", wsComfyUrl);
        statusEl.textContent = "Connected to ComfyUI";
      };
      
      wsComfy.onmessage = function(event) {
        console.log("Received message from ComfyUI");
        
        if (event.data instanceof Blob) {
          // This is binary image data
          console.log("Received image data from ComfyUI");
          const blobUrl = URL.createObjectURL(event.data);
          imgEl.src = blobUrl;
          
          // If recording frames, save this frame
          if (isRecordingFrames) {
            saveFrameFromImageElement();
          }
        } else if (typeof event.data === "string") {
          try {
            const message = JSON.parse(event.data);
            console.log("ComfyUI message:", message);
            
            // Update execution info for status messages
            if (message.type === "executing") {
              if (message.data.node === null) {
                executionInfo.textContent = "Workflow execution completed!";
              } else {
                executionInfo.textContent = `Executing node: ${message.data.node}`;
              }
            } else if (message.type === "status") {
              workflowStatus.textContent = `Status: ${message.data.status}`;
            }
          } catch (e) {
            console.log("Non-JSON message from ComfyUI:", event.data);
          }
        }
      };
      
      wsComfy.onerror = function(error) {
        console.error("ComfyUI WebSocket error:", error);
        statusEl.textContent = "ComfyUI connection error";
      };
      
      wsComfy.onclose = function(event) {
        console.log("ComfyUI WebSocket closed. Code:", event.code, "Reason:", event.reason);
        statusEl.textContent = "ComfyUI connection closed";
        
        // Reconnect after a delay
        setTimeout(connectToComfyWebSocket, 5000);
      };
    }
    
    // WebSocket handling for Sphinx emotion data
    let wsSphinx = null;
    
    function connectToSphinxWebSocket() {
      wsSphinx = new WebSocket(wsSphinxUrl);
      wsSphinx.binaryType = "arraybuffer";
      
      wsSphinx.onopen = function() {
        console.log("Connected to Sphinx WebSocket:", wsSphinxUrl);
      };
      
      wsSphinx.onmessage = function(event) {
        if (typeof event.data === "string") {
          try {
            const data = JSON.parse(event.data);
            if (data.emotions) {
              const emotionsText = Object.entries(data.emotions)
                .map(([emotion, score]) => `${emotion}: ${(score * 100).toFixed(1)}%`)
                .join('<br>');
              emotionsEl.innerHTML = emotionsText;
            }
            // Note: We're now handling images from the direct ComfyUI connection
          } catch (e) {
            console.log("Received text message from Sphinx:", event.data);
            if (event.data.trim().toLowerCase() === "ping") {
              return;
            }
          }
        }
      };
      
      wsSphinx.onerror = function(error) {
        console.error("Sphinx WebSocket error:", error);
      };
      
      wsSphinx.onclose = function(event) {
        console.log("Sphinx WebSocket closed. Code:", event.code, "Reason:", event.reason);
        
        // Reconnect after a delay
        setTimeout(connectToSphinxWebSocket, 5000);
      };
    }
    
    // Call API to trigger workflow
    triggerWorkflowBtn.addEventListener('click', function() {
      workflowStatus.textContent = 'Triggering workflow...';
      
      fetch(`${apiServerUrl}/trigger_workflow`, {
        method: 'POST'
      })
      .then(response => response.json())
      .then(data => {
        workflowStatus.textContent = `Workflow ${data.status}: ${data.message}`;
        if (data.prompt) {
          workflowStatus.textContent += ` (Prompt: ${data.prompt})`;
        }
      })
      .catch(error => {
        workflowStatus.textContent = `Error: ${error}`;
        console.error('Error triggering workflow:', error);
      });
    });
    
    // Frame recording event listeners
    startFrameRecordingBtn.addEventListener('click', toggleFrameRecording);
    saveFramesBtn.addEventListener('click', saveFrames);
    clearFramesBtn.addEventListener('click', clearFrames);
    
    function updateServers() {
      const apiInput = document.getElementById('apiServer');
      const wsInput = document.getElementById('wsServer');
      
      apiServerUrl = apiInput.value;
      wsServerUrl = wsInput.value;
      
      localStorage.setItem('apiServerUrl', apiServerUrl);
      localStorage.setItem('wsServerUrl', wsServerUrl);
      
      recordingStatus.textContent = 'Server settings updated. Please refresh the page to connect to new servers.';
    }
    
    // Initialize everything
    document.getElementById('apiServer').value = apiServerUrl;
    document.getElementById('wsServer').value = wsServerUrl;
    setupAudioRecording();
    connectToComfyWebSocket();
    connectToSphinxWebSocket();
    
    // Load JSZip library for saving recordings
    const jsZipScript = document.createElement('script');
    jsZipScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
    jsZipScript.integrity = 'sha512-XMVd28F1oH/O71fzwBnV7HucLxVwtxf26XV8P4wPk26EDxuGZ91N8bsOyYE5PdgJRm4/auX1UnLhwmgJ+A/Wg==';
    jsZipScript.crossOrigin = 'anonymous';
    document.head.appendChild(jsZipScript);
  </script>
</body>
</html>
"""
    
    return html_content

@app.get("/stream_client", response_class=HTMLResponse)
async def stream_client():
    """
    Serves the existing client.html with the correct WebSocket URL and client ID.
    """
    # Use the known path to client.html
    client_path = "/client/client.html"
    
    if not os.path.exists(client_path):
        return "Client HTML file not found at /client/client.html"
    
    # Read the file
    with open(client_path, "r") as f:
        client_html = f.read()
    
    # Get the most recent client ID
    client_id = str(uuid.uuid4())  # Default
    prompt_id = ""
    try:
        if os.path.exists("/workspace/app/last_prompt.json"):
            with open("/workspace/app/last_prompt.json", "r") as f:
                prompt_info = json.load(f)
                client_id = prompt_info.get("client_id", client_id)
                prompt_id = prompt_info.get("prompt_id", "")
    except Exception as e:
        print(f"Error reading last prompt info: {e}")
    
    # Create a script element to inject into the HTML
    ws_script = f"""
    <script>
        // Override WebSocket settings with RunPod values
        window.wsUrl = "wss://dlz1l9gphefry5-3020.proxy.runpod.net/ws";
        window.clientId = "{client_id}";
        console.log("Using WebSocket:", window.wsUrl + "?clientId=" + window.clientId);
    </script>
    """
    
    # Insert our script at the end of the head section
    if "<head>" in client_html:
        modified_html = client_html.replace("</head>", f"{ws_script}</head>")
    else:
        # If no head section, add it at the top of the body
        if "<body>" in client_html:
            modified_html = client_html.replace("<body>", f"<body>{ws_script}")
        else:
            # Fallback - add at the beginning of the file
            modified_html = f"{ws_script}{client_html}"
    
    return modified_html

@app.get("/original_client", response_class=HTMLResponse)
async def original_client():
    """
    Creates an exact copy of the original client.html which we know works for audio recording.
    """
    try:
        # Use the known path to client.html
        client_path = "/client/client.html"
        
        if not os.path.exists(client_path):
            return "Client HTML file not found at /client/client.html"
        
        # Read the file and return it unchanged
        with open(client_path, "r") as f:
            client_html = f.read()
        
        return client_html
        
    except Exception as e:
        return f"Error loading original client: {str(e)}"

@app.get("/image_viewer", response_class=HTMLResponse)
async def image_viewer():
    """
    Creates a minimal client that only connects to ComfyUI WebSocket to display images.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ComfyUI Image Viewer</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    img { max-width: 100%; border: 1px solid #ccc; }
    button { 
      padding: 10px 20px; 
      margin: 5px; 
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover {
      background-color: #45a049;
    }
    #log {
      background-color: #f8f8f8;
      border: 1px solid #ccc;
      font-family: monospace;
      height: 200px;
      overflow-y: auto;
      padding: 5px;
      margin-top: 10px;
    }
    #status {
      font-weight: bold;
    }
  </style>
</head>
<body>
  <h1>ComfyUI Image Viewer</h1>
  <p>Status: <span id="status">Disconnected</span></p>
  
  <div>
    <button id="triggerBtn">Trigger Workflow</button>
    <span id="triggerStatus"></span>
  </div>
  
  <div style="margin-top: 20px;">
    <h2>Received Image:</h2>
    <img id="image" src="" alt="Waiting for image...">
  </div>
  
  <div>
    <h2>Connection Log:</h2>
    <div id="log"></div>
  </div>

  <script>
    // Fixed client ID - must match the one in workflow_manager.py
    const clientId = "sphinx_api_client";
    
    // WebSocket URL
    const wsUrl = "wss://dlz1l9gphefry5-3020.proxy.runpod.net/ws?clientId=" + clientId;
    
    // UI elements
    const statusEl = document.getElementById('status');
    const imageEl = document.getElementById('image');
    const logEl = document.getElementById('log');
    const triggerBtn = document.getElementById('triggerBtn');
    const triggerStatusEl = document.getElementById('triggerStatus');
    
    // Log function
    function log(message) {
      const entry = document.createElement('div');
      entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
      logEl.appendChild(entry);
      logEl.scrollTop = logEl.scrollHeight;
      console.log(message);
    }
    
    // Connect to ComfyUI WebSocket
    let ws = null;
    
    function connect() {
      log("Connecting to " + wsUrl);
      statusEl.textContent = "Connecting...";
      
      ws = new WebSocket(wsUrl);
      ws.binaryType = "arraybuffer";
      
      ws.onopen = function() {
        log("Connected to ComfyUI WebSocket");
        statusEl.textContent = "Connected";
      };
      
      ws.onmessage = function(event) {
        if (event.data instanceof ArrayBuffer) {
          log("Received binary image data");
          
          // Skip the first 8 bytes which are metadata in SaveImageWebsocket format
          const imageData = new Uint8Array(event.data).slice(8);
          
          // Create a blob from the image data
          const blob = new Blob([imageData], {type: 'image/png'});
          
          // Update the image
          imageEl.src = URL.createObjectURL(blob);
        } else if (typeof event.data === "string") {
          try {
            const message = JSON.parse(event.data);
            log(`Received message: ${JSON.stringify(message)}`);
            
            if (message.type === "executing") {
              if (message.data.node) {
                log(`Executing node: ${message.data.node}`);
              } else {
                log("Execution complete");
              }
            }
          } catch (e) {
            log(`Received text: ${event.data}`);
          }
        }
      };
      
      ws.onclose = function(event) {
        log(`WebSocket closed: Code ${event.code}`);
        statusEl.textContent = "Disconnected";
        
        // Try to reconnect after a delay
        setTimeout(connect, 5000);
      };
      
      ws.onerror = function(error) {
        log("WebSocket error");
        console.error(error);
        statusEl.textContent = "Connection error";
      };
    }
    
    // Trigger workflow button
    triggerBtn.addEventListener('click', function() {
      triggerStatusEl.textContent = "Triggering workflow...";
      log("Triggering workflow via API");
      
      fetch('https://dlz1l9gphefry5-8010.proxy.runpod.net/trigger_workflow', {
        method: 'POST'
      })
      .then(response => response.json())
      .then(data => {
        triggerStatusEl.textContent = `${data.status}: ${data.message}`;
        log(`Workflow triggered: ${data.status} - ${data.message}`);
      })
      .catch(error => {
        triggerStatusEl.textContent = `Error: ${error}`;
        log(`Error triggering workflow: ${error}`);
      });
    });
    
    // Connect when the page loads
    connect();
  </script>
</body>
</html>
"""
    
    return html_content

@app.get("/working_client", response_class=HTMLResponse)
async def working_client():
    """
    A focused client that correctly displays transcription and emotions,
    with connection logging and improved image fetching.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Audio & Image Client</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; max-width: 1200px; margin: 0 auto; padding-bottom: 30px; }
    img { max-width: 100%; border: 1px solid #ccc; max-height: 500px; }
    button {
      padding: 10px 20px;
      margin: 5px;
      border-radius: 5px;
      cursor: pointer;
      background-color: #4CAF50;
      color: white;
      border: none;
    }
    .recording { background-color: #ff4444; }
    .section {
      margin: 10px 0;
      padding: 15px;
      background-color: #f9f9f9;
      border-radius: 5px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .data-display {
      min-height: 40px;
      padding: 10px;
      background-color: white;
      border-radius: 3px;
      border: 1px solid #ddd;
      margin-top: 5px;
    }
    #log {
      background-color: #f8f8f8;
      border: 1px solid #ccc;
      font-family: monospace;
      height: 150px;
      overflow-y: auto;
      padding: 5px;
      margin-top: 10px;
    }
    h3 { margin-top: 0; }
  </style>
</head>
<body>
  <h1>Audio & Image Generation Client</h1>
  
  <div class="section">
    <h3>Connection Status</h3>
    <p>ComfyUI WebSocket: <span id="comfyStatus">Connecting...</span></p>
    <div id="log"></div>
  </div>
  
  <div class="section">
    <h3>Audio Recording</h3>
    <button id="recordButton">Record Audio (10s)</button>
    <button id="triggerWorkflowBtn">Trigger Workflow</button>
    <button id="refreshImageBtn">Refresh Image</button>
    <span id="recordingStatus"></span>
  </div>
  
  <div class="section">
    <h3>Transcription</h3>
    <div id="transcriptionDisplay" class="data-display">Waiting for audio recording...</div>
  </div>
  
  <div class="section">
    <h3>Detected Emotions</h3>
    <div id="emotionsDisplay" class="data-display">Waiting for emotions data...</div>
  </div>
  
  <div class="section">
    <h3>Generated Image</h3>
    <img id="streamedImage" src="" alt="Waiting for image...">
  </div>

  <script>
    // Config
    const apiServerUrl = 'https://dlz1l9gphefry5-8010.proxy.runpod.net';
    const wsServerUrl = 'dlz1l9gphefry5-3020.proxy.runpod.net';
    const clientId = "sphinx_api_client";
    
    // WebSocket URLs
    const wsComfyUrl = `wss://${wsServerUrl}/ws?clientId=${clientId}`;
    
    // UI elements
    const imgEl = document.getElementById("streamedImage");
    const emotionsEl = document.getElementById("emotionsDisplay");
    const transcriptionEl = document.getElementById("transcriptionDisplay");
    const recordButton = document.getElementById("recordButton");
    const recordingStatus = document.getElementById("recordingStatus");
    const triggerWorkflowBtn = document.getElementById("triggerWorkflowBtn");
    const refreshImageBtn = document.getElementById("refreshImageBtn");
    const comfyStatusEl = document.getElementById("comfyStatus");
    const logEl = document.getElementById("log");
    
    // Variables
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let imageFetchAttempts = 0;
    const maxImageFetchAttempts = 5;
    
    // Log function
    function log(message) {
      const entry = document.createElement('div');
      entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
      logEl.appendChild(entry);
      logEl.scrollTop = logEl.scrollHeight;
      console.log(message);
    }
    
    // Audio recording
    async function setupAudioRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          log('Audio recorded, size: ' + audioBlob.size + ' bytes');
          await sendAudioToServer(audioBlob);
          audioChunks = [];
        };
        
        recordButton.addEventListener('click', toggleRecording);
        log("Audio recording setup complete");
      } catch (err) {
        console.error('Error accessing microphone:', err);
        recordingStatus.textContent = 'Error: Could not access microphone';
        log('Error accessing microphone: ' + err);
      }
    }
    
    function toggleRecording() {
      if (!isRecording) {
        mediaRecorder.start();
        recordButton.textContent = 'Stop Recording';
        recordButton.classList.add('recording');
        recordingStatus.textContent = 'Recording...';
        isRecording = true;
        
        // Automatically stop recording after 10 seconds
        setTimeout(() => {
          if (isRecording) {
            log("Auto-stopping recording after 10 seconds");
            toggleRecording();
          }
        }, 10000);
      } else {
        mediaRecorder.stop();
        recordButton.textContent = 'Record Audio (10s)';
        recordButton.classList.remove('recording');
        recordingStatus.textContent = 'Processing...';
        isRecording = false;
      }
    }
    
    async function sendAudioToServer(audioBlob) {
      const formData = new FormData();
      formData.append('file', audioBlob);
      
      try {
        log('Sending audio to server for processing');
        recordingStatus.textContent = 'Sending audio to server...';
        
        const response = await fetch(`${apiServerUrl}/transcribe_and_generate`, {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        log("Received API response with transcription and emotions");
        
        // Update UI with the response data
        if (data.transcription) {
          transcriptionEl.textContent = data.transcription;
          log("Transcription: " + data.transcription);
        }
        
        if (data.emotions) {
          const emotionsText = Object.entries(data.emotions)
            .map(([emotion, score]) => `${emotion}: ${(score * 100).toFixed(1)}%`)
            .join('<br>');
          emotionsEl.innerHTML = emotionsText;
          log("Emotions received: " + Object.keys(data.emotions).join(", "));
        }
        
        recordingStatus.textContent = 'Transcription and emotion analysis complete!';
        
        // After processing is complete, start checking for the image
        log("Starting image fetch attempts");
        imageFetchAttempts = 0;
        fetchLatestImageWithRetry();
      } catch (error) {
        console.error('Error sending audio:', error);
        log('Error processing audio: ' + error);
        recordingStatus.textContent = 'Error processing audio';
      }
    }
    
    // Fetch latest image with retry mechanism
    function fetchLatestImageWithRetry() {
      imageFetchAttempts++;
      log(`Fetching latest image (attempt ${imageFetchAttempts}/${maxImageFetchAttempts})`);
      recordingStatus.textContent = `Fetching image (attempt ${imageFetchAttempts})...`;
      
      // Add timestamp to prevent caching
      const timestamp = Date.now();
      const tempImage = new Image();
      tempImage.onload = function() {
        log("Image fetched successfully!");
        imgEl.src = this.src;
        recordingStatus.textContent = 'Image generated successfully!';
      };
      
      tempImage.onerror = function() {
        log(`Image fetch attempt ${imageFetchAttempts} failed`);
        if (imageFetchAttempts < maxImageFetchAttempts) {
          // Try again after a delay that increases with each attempt
          const delay = 3000 + (imageFetchAttempts * 2000);
          log(`Retrying in ${delay/1000} seconds...`);
          recordingStatus.textContent = `Image not ready, retrying in ${delay/1000}s...`;
          setTimeout(fetchLatestImageWithRetry, delay);
        } else {
          log("Max retry attempts reached");
          recordingStatus.textContent = 'Could not fetch image after multiple attempts';
        }
      };
      
      tempImage.src = `${apiServerUrl}/latest_image?t=${timestamp}`;
    }
    
    // Refresh image button
    refreshImageBtn.addEventListener('click', function() {
      log("Manually refreshing image");
      recordingStatus.textContent = 'Refreshing image...';
      imageFetchAttempts = 0;
      fetchLatestImageWithRetry();
    });
    
    // Trigger workflow button
    triggerWorkflowBtn.addEventListener('click', function() {
      log("Manually triggering workflow");
      recordingStatus.textContent = 'Triggering workflow...';
      
      fetch(`${apiServerUrl}/trigger_workflow`, {
        method: 'POST'
      })
      .then(response => response.json())
      .then(data => {
        log(`Workflow response: ${data.status} - ${data.message}`);
        recordingStatus.textContent = `Workflow: ${data.status} - ${data.message}`;
        
        // Start checking for the image
        imageFetchAttempts = 0;
        setTimeout(fetchLatestImageWithRetry, 3000);
      })
      .catch(error => {
        log(`Error triggering workflow: ${error}`);
        recordingStatus.textContent = `Error: ${error}`;
      });
    });
    
    // Connect to ComfyUI WebSocket for live images
    function connectToComfyWs() {
      log("Connecting to ComfyUI WebSocket: " + wsComfyUrl);
      comfyStatusEl.textContent = "Connecting...";
      const ws = new WebSocket(wsComfyUrl);
      ws.binaryType = "arraybuffer";
      
      ws.onopen = function() {
        log("Connected to ComfyUI WebSocket");
        comfyStatusEl.textContent = "Connected";
        comfyStatusEl.style.color = "green";
      };
      
      ws.onmessage = function(event) {
        if (event.data instanceof ArrayBuffer) {
          log("Received binary image data from ComfyUI WebSocket");
          
          // Skip the first 8 bytes which are metadata
          const imageData = new Uint8Array(event.data).slice(8);
          
          // Create a blob from the image data
          const blob = new Blob([imageData], {type: 'image/png'});
          
          // Update the image
          imgEl.src = URL.createObjectURL(blob);
          recordingStatus.textContent = 'New image received from ComfyUI!';
        } else if (typeof event.data === "string") {
          try {
            const message = JSON.parse(event.data);
            if (message.type === "executing") {
              if (message.data.node) {
                log(`ComfyUI executing node: ${message.data.node}`);
              } else {
                log("ComfyUI execution complete");
              }
            } else {
              log("ComfyUI message: " + JSON.stringify(message).substring(0, 100));
            }
          } catch (e) {
            log("ComfyUI text message: " + event.data);
          }
        }
      };
      
      ws.onclose = function() {
        log("ComfyUI WebSocket closed - reconnecting in 5 seconds");
        comfyStatusEl.textContent = "Disconnected";
        comfyStatusEl.style.color = "red";
        setTimeout(connectToComfyWs, 5000);
      };
      
      ws.onerror = function(error) {
        log("ComfyUI WebSocket error");
        comfyStatusEl.textContent = "Error";
        comfyStatusEl.style.color = "red";
        console.error(error);
      };
    }
    
    // Initialize
    setupAudioRecording();
    connectToComfyWs();
    log("Client initialized");
  </script>
</body>
</html>
"""
    
    return html_content

@app.post("/process_audio")
async def process_audio(audio_data: bytes = File(...)):
    """
    Process recorded audio and trigger the workflow with the resulting emotion data.
    """
    global latest_emotion_scores
    
    try:
        # Save the audio temporarily
        audio_path = "/tmp/audio.webm"
        with open(audio_path, "wb") as f:
            f.write(audio_data)
        
        print(f"Audio recorded, size: {len(audio_data)} bytes")
        
        # Process the audio with your API
        print("Sending audio to server for processing")
        result = process_audio_file(audio_path)
        
        # Extract transcription and emotions
        transcription = result.get("transcription", "")
        emotions = result.get("emotions", {})
        
        print(f"Transcription: {transcription}")
        print(f"Emotions received: {', '.join(emotions.keys())}")
        
        # Store the latest emotion data for the EmotionImportNode
        latest_emotion_scores = emotions
        
        # AUTOMATICALLY TRIGGER THE WORKFLOW
        print("Automatically triggering workflow with new emotions")
        try:
            # Get the best ComfyUI URL
            comfyui_url = workflow_manager.test_comfyui_connection()
            print(f"Using ComfyUI URL: {comfyui_url}")
            
            # Trigger the workflow with the new emotions
            thread = workflow_manager.run_workflow_with_custom_nodes(comfyui_url)
            print("Workflow triggered successfully in background")
        except Exception as e:
            print(f"Error triggering workflow: {e}")
            import traceback
            traceback.print_exc()
        
        return {"status": "success", "transcription": transcription, "emotions": emotions}
    
    except Exception as e:
        print(f"Error processing audio: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
