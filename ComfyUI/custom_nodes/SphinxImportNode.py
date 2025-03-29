# SphinxImportNode.py - Unified importer for Sphinx data
import requests
import time
import threading

# Global variables
latest_emotion_scores = {}
latest_transformation = {"from": "Uncertainty", "to": "Confidence"}

def trigger_workflow():
    """Trigger the workflow execution via the API endpoint"""
    try:
        response = requests.post('http://127.0.0.1:8010/trigger_workflow')
        if response.status_code == 200:
            print("✅ Successfully triggered workflow execution", flush=True)
        else:
            print(f"⚠️ Failed to trigger workflow: {response.status_code}", flush=True)
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}", flush=True)

def fetch_data():
    """Fetch both emotion and transformation data from Sphinx API"""
    global latest_emotion_scores, latest_transformation
    emotions_url = "http://127.0.0.1:8010/get_emotion_data"
    transformation_url = "http://127.0.0.1:8010/latest_transformation"
    last_trigger_time = 0
    min_trigger_interval = 5  # seconds
    
    while True:
        try:
            # Get emotions
            response = requests.get(emotions_url)
            if response.status_code == 200:
                data = response.json()
                new_emotions = data.get("emotions", {})
                current_time = time.time()
                
                if new_emotions != latest_emotion_scores and current_time - last_trigger_time >= min_trigger_interval:
                    latest_emotion_scores = new_emotions
                    print("✅ Updated emotion data:", latest_emotion_scores, flush=True)
                    trigger_workflow()
                    last_trigger_time = current_time
            
            # Get transformation
            try:
                trans_response = requests.get(transformation_url)
                if trans_response.status_code == 200:
                    trans_data = trans_response.json()
                    if trans_data and trans_data.get("status") == "success":
                        # Handle different response formats
                        if "transformation" in trans_data:
                            # Format from latest_transformation endpoint
                            transform_data = trans_data.get("transformation", {})
                            latest_transformation = {
                                "from": transform_data.get("from", "Uncertainty"),
                                "to": transform_data.get("to", "Confidence")
                            }
                        else:
                            # Format from latest_media or other endpoints
                            latest_transformation = {
                                "from": trans_data.get("from", "Uncertainty"),
                                "to": trans_data.get("to", "Confidence")
                            }
                        print(f"✅ Updated transformation: {latest_transformation}", flush=True)
            except:
                pass  # Silently continue if transformation endpoint isn't available yet
                
        except Exception as e:
            print(f"❌ Error fetching data: {e}", flush=True)
            
        time.sleep(3)

# Start the background thread to poll the API
threading.Thread(target=fetch_data, daemon=True).start()

class SphinxImportNode:
    """
    A ComfyUI node that imports both emotion and transformation data from the Sphinx API.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("DICT", "STRING", "STRING")
    RETURN_NAMES = ("emotion_scores", "from_state", "to_state")
    FUNCTION = "get_sphinx_data"
    CATEGORY = "Sphinx"

    def get_sphinx_data(self):
        return (
            latest_emotion_scores, 
            latest_transformation.get("from", "Uncertainty"),
            latest_transformation.get("to", "Confidence")
        )

NODE_CLASS_MAPPINGS = {
    "SphinxImportNode": SphinxImportNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SphinxImportNode": "Sphinx Import (Emotions & Transformations)"
} 