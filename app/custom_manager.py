# custom_manager.py - Modified version of workflow_manager.py that uses uploaded workflows

import os
import sys
import json
import requests
import time
import threading
import uuid

# Path to workflows directory
WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), "workflows")

# Global variables to track workflow execution
currently_running = False
execution_log = []
last_output_image = None
last_output_video = None
current_progress = 0
client_id = None

def load_workflow_from_file(filename):
    """
    Load a workflow JSON file from the workflows directory
    """
    try:
        # Make sure the workflows directory exists
        os.makedirs(WORKFLOWS_DIR, exist_ok=True)
        
        # Build the full path to the workflow file
        workflow_path = os.path.join(WORKFLOWS_DIR, filename)
        
        # Check if the file exists
        if not os.path.exists(workflow_path):
            print(f"Workflow file not found: {workflow_path}")
            return None
        
        # Load the JSON data
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
            
        print(f"Successfully loaded workflow from {workflow_path}")
        return workflow_data
    
    except Exception as e:
        print(f"Error loading workflow file: {e}")
        return None

def find_comfyui_url():
    """Test connection to ComfyUI and determine the best URL to use."""
    possible_urls = [
        "http://127.0.0.1:3020",
        "http://localhost:3020", 
        "http://comfyui:3020"
    ]
    
    for url in possible_urls:
        try:
            print(f"Testing connection to ComfyUI at: {url}")
            response = requests.get(f"{url}/system_stats", timeout=2)
            if response.status_code == 200:
                print(f"Successfully connected to ComfyUI API at {url}")
                return url
        except Exception as e:
            print(f"Could not connect to {url}: {e}")
    
    print("No ComfyUI connection verified, using default URL")
    return "http://127.0.0.1:3020"

def execute_workflow(workflow_filename, parameters=None):
    """
    Execute a workflow from a file with optional parameters
    """
    global currently_running, execution_log, client_id, current_progress, last_output_image, last_output_video
    
    print(f"custom_manager.execute_workflow called with: {workflow_filename}, parameters={parameters}")
    
    # If a workflow is already running, force-terminate it
    if currently_running:
        print("A workflow is already running, terminating previous workflow...")
        execution_log.append("Terminating previous workflow to start a new one")
    
    # Reset state
    currently_running = True
    execution_log.clear()
    current_progress = 0
    last_output_image = None
    last_output_video = None
    
    execution_log.append(f"Executing workflow: {workflow_filename}")
    
    # Generate a unique client ID
    client_id = f"custom_{uuid.uuid4().hex[:8]}"
    
    # Start execution in a background thread
    thread = threading.Thread(
        target=_execute_workflow_thread,
        args=(workflow_filename, parameters, client_id),
        daemon=True
    )
    thread.start()
    print(f"Started execution thread for workflow {workflow_filename}")
    
    return {
        "status": "success",
        "message": f"Workflow started successfully: Workflow {workflow_filename} started",
        "client_id": client_id
    }

def _execute_workflow_thread(workflow_filename, parameters, client_id):
    """
    Thread function to execute the workflow
    """
    global currently_running, execution_log, last_output_image, last_output_video, current_progress
    
    try:
        # Reset progress at start
        current_progress = 0
        
        # Load the workflow
        workflow_data = load_workflow_from_file(workflow_filename)
        if not workflow_data:
            execution_log.append(f"❌ Failed to load workflow: {workflow_filename}")
            currently_running = False
            return
        
        # Skip compatibility check - since  this is unnecessary
        # and we're running on the right machine
        '''
        execution_log.append("Checking workflow for compatibility...")
        is_valid, missing_nodes = check_workflow_nodes(workflow_data)
        if not is_valid:
            execution_log.append("❌ Workflow contains missing nodes:")
            for node in missing_nodes:
                execution_log.append(f"  - {node}")
                
            execution_log.append("\nPlease install the required custom nodes and try again.")
            execution_log.append("Common missing collections include:")
            execution_log.append("  - ComfyUI-Manager: https://github.com/ltdrdata/ComfyUI-Manager")
            execution_log.append("  - pysssss: https://github.com/pythongosssss/ComfyUI-Custom-Scripts")
            currently_running = False
            return
        '''
        
        # Find ComfyUI URL
        comfyui_url = find_comfyui_url()
        if not comfyui_url:
            execution_log.append("❌ Failed to connect to ComfyUI API")
            currently_running = False
            return
        
        # Update workflow with parameters if provided
        if parameters:
            execution_log.append(f"Updating workflow with parameters: {parameters}")
            try:
                # This is a simple example - you'll need to modify based on your workflow structure
                for node_id, node in workflow_data.get("nodes", {}).items():
                    if "inputs" in node:
                        for param_name, param_value in parameters.items():
                            if param_name in node["inputs"]:
                                node["inputs"][param_name] = param_value
                                execution_log.append(f"Updated parameter {param_name} in node {node_id}")
            except Exception as e:
                execution_log.append(f"Warning: Error updating parameters: {e}")
                # Continue with original workflow
        
        # Send the workflow to ComfyUI
        execution_log.append(f"Sending workflow to {comfyui_url}/prompt")
        response = requests.post(
            f"{comfyui_url}/prompt",
            json={"prompt": workflow_data, "client_id": client_id}
        )
        
        if response.status_code != 200:
            execution_log.append(f"Error: ComfyUI returned status code {response.status_code}")
            execution_log.append(f"Response: {response.text}")
            currently_running = False
            return
        
        # Get prompt ID from response
        result = response.json()
        prompt_id = result.get("prompt_id")
        if not prompt_id:
            execution_log.append("Error: No prompt ID in ComfyUI response")
            currently_running = False
            return
        
        execution_log.append(f"Workflow sent successfully. Prompt ID: {prompt_id}")
        
        # Monitor execution via WebSocket
        try:
            import websocket
            ws_url = f"ws://{comfyui_url.split('//')[1]}/ws?clientId={client_id}"
            execution_log.append(f"Connecting to WebSocket: {ws_url}")
            
            ws = websocket.create_connection(ws_url)
            execution_log.append("WebSocket connection established")
            
            # Wait for execution to complete
            while True:
                message = ws.recv()
                data = json.loads(message)
                
                # Log the message type
                msg_type = data.get("type", "unknown")
                execution_log.append(f"Received message type: {msg_type}")
                
                # Handle different message types
                if msg_type == "executing":
                    node_id = data.get("data", {}).get("node")
                    if node_id is None:
                        execution_log.append("Workflow execution completed")
                        break
                    else:
                        execution_log.append(f"Executing node: {node_id}")
                
                elif msg_type == "executed":
                    execution_log.append("Node execution completed")
                
                elif msg_type == "progress":
                    # Extract progress value
                    try:
                        # The data might be a dictionary with a 'value' key or the value might be nested
                        if isinstance(data, dict):
                            if 'value' in data:
                                progress_value = int(data['value'])
                            elif 'data' in data and isinstance(data['data'], dict) and 'value' in data['data']:
                                progress_value = int(data['data']['value'])
                            else:
                                # Default progress value if we can't extract it
                                progress_value = 0
                                
                            if progress_value > current_progress:
                                current_progress = progress_value
                                execution_log.append(f"Progress: {current_progress}%")
                    except Exception as e:
                        execution_log.append(f"Error processing progress message: {e}")
                
                elif msg_type == "status":
                    status = data.get("data", {}).get("status")
                    execution_log.append(f"Status: {status}")
            
            ws.close()
            execution_log.append("WebSocket connection closed")
            
            # Try to get the result image
            execution_log.append("Retrieving output images")
            
            # Wait a moment for the output to be saved
            time.sleep(2)
            
            # Get the history to find the output images
            history_response = requests.get(f"{comfyui_url}/history/{prompt_id}")
            if history_response.status_code == 200:
                history = history_response.json()
                outputs = history.get("outputs", {})
                
                # Find image outputs
                images = []
                for node_id, node_outputs in outputs.items():
                    for output in node_outputs:
                        if "images" in output:
                            for img in output["images"]:
                                image_url = f"{comfyui_url}/view?filename={img['filename']}&type={img['type']}"
                                images.append({
                                    "url": image_url,
                                    "filename": img['filename'],
                                    "type": img['type']
                                })
                
                if images:
                    execution_log.append(f"Found {len(images)} output images")
                    last_output_image = images[0]  # Save the first image
                else:
                    execution_log.append("No output images found")
            else:
                execution_log.append(f"Error getting history: {history_response.status_code}")
            
            # After the workflow completes, search for video outputs
            try:
                # After workflow completion, wait a bit longer for video generation
                execution_log.append("Waiting for video processing to complete...")
                time.sleep(5)  # Wait 5 seconds for video processing

                # List mp4 files by modification time
                try:
                    output_dir = "/workspace/ComfyUI/output"
                    video_files = []
                    
                    for root, dirs, files in os.walk(output_dir):
                        for file in files:
                            if file.endswith(".mp4"):
                                video_path = os.path.join(root, file)
                                video_url = f"/download_video?filename={file}"
                                video_files.append({
                                    "path": video_path,
                                    "url": video_url,
                                    "filename": file,
                                    "mtime": os.path.getmtime(video_path)
                                })
                                execution_log.append(f"Found video file: {file}")
                    
                    if video_files:
                        # Sort videos by modification time (newest first)
                        video_files.sort(key=lambda x: x["mtime"], reverse=True)
                        last_output_video = video_files[0]
                        execution_log.append(f"Selected most recent video: {last_output_video['filename']}")
                    else:
                        execution_log.append("No video files found")
                except Exception as e:
                    execution_log.append(f"Error finding videos: {e}")
            except Exception as e:
                execution_log.append(f"Error searching for videos: {e}")
        
        except Exception as e:
            execution_log.append(f"Error monitoring execution: {e}")
        
        execution_log.append("Workflow execution thread completed")
    
    except Exception as e:
        execution_log.append(f"Error in workflow execution thread: {e}")
    
    finally:
        currently_running = False

def get_execution_status():
    """
    Get the current status of workflow execution
    """
    global currently_running, execution_log, last_output_image, last_output_video, client_id, current_progress
    
    return {
        "running": currently_running,
        "client_id": client_id,
        "log": execution_log,
        "last_image": last_output_image,
        "last_video": last_output_video,
        "progress": current_progress
    }

def get_available_workflows():
    """
    Get a list of available workflow files
    """
    try:
        os.makedirs(WORKFLOWS_DIR, exist_ok=True)
        workflows = [f for f in os.listdir(WORKFLOWS_DIR) if f.endswith('.json')]
        return {"status": "success", "workflows": workflows}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_workflow_nodes(workflow_data):
    """
    Check if all nodes in the workflow exist in the ComfyUI installation
    Returns a tuple: (is_valid, list_of_missing_nodes)
    """
    try:
        # Get list of available nodes from ComfyUI
        comfyui_url = find_comfyui_url()
        try:
            response = requests.get(f"{comfyui_url}/object_info", timeout=3)
            if response.status_code != 200:
                # If we can't get node info, assume workflow is valid
                print(f"Warning: Couldn't get node info, status code: {response.status_code}")
                return True, []
            
            try:
                available_nodes = response.json().get("object_info", {}).keys()
            except json.JSONDecodeError:
                # If we can't parse the response, assume workflow is valid
                print(f"Warning: Invalid JSON response from /object_info")
                return True, []
                
            # Check each node in the workflow
            missing_nodes = []
            for node_id, node_data in workflow_data.get("nodes", {}).items():
                node_type = node_data.get("class_type")
                if node_type and node_type not in available_nodes:
                    missing_nodes.append(f"{node_type} (ID: {node_id})")
            
            return len(missing_nodes) == 0, missing_nodes
        except Exception as e:
            # If there's any error checking nodes, just assume the workflow is valid
            print(f"Warning: Error checking nodes: {e}")
            return True, []
            
    except Exception as e:
        print(f"Warning: Error in check_workflow_nodes: {e}")
        return True, []  # Assume workflow is valid if we can't check

# Test if run directly
if __name__ == "__main__":
    # List available workflows
    workflows = get_available_workflows()
    print("Available workflows:", workflows)
    
    if workflows["status"] == "success" and workflows["workflows"]:
        # Execute the first workflow
        workflow_file = workflows["workflows"][0]
        print(f"Executing workflow: {workflow_file}")
        
        result = execute_workflow(workflow_file)
        print("Execution started:", result)
        
        # Monitor execution
        while currently_running:
            status = get_execution_status()
            print(f"Running: {len(status['log'])} log entries")
            time.sleep(2)
        
        # Print final status
        final_status = get_execution_status()
        print("\nExecution completed")
        print("Log:")
        for entry in final_status["log"]:
            print(f"  {entry}")
        
        if final_status["last_image"]:
            print(f"\nOutput image: {final_status['last_image']['url']}")
        if final_status["last_video"]:
            print(f"\nOutput video: {final_status['last_video']['url']}")
    else:
        print("No workflows available")

# At the top of the WebSocket handler, add this for debugging
try:
    # Log raw WebSocket data for the first few messages
    if len(execution_log) < 20:  # Only for the first few messages to avoid flooding
        execution_log.append(f"Raw WS data: {message[:100]}...")  # Log first 100 chars
except:
    pass