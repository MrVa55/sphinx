import requests
import time
import threading
import global_vars
import json
import os

# Global variables
latest_emotion_scores = {}
latest_transformation = {"from": "Uncertainty", "to": "Confidence"}  # Default values
last_processed_scores = None

def trigger_workflow():
    """Trigger the workflow execution via the API endpoint"""
    try:
        response = requests.post('http://127.0.0.1:8010/trigger_workflow')
        if response.status_code == 200:
            print("✅ Successfully triggered workflow execution", flush=True)
        else:
            print(f"⚠️ Failed to trigger workflow: {response.status_code}", flush=True)
            print(f"Response content: {response.text}", flush=True)
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}", flush=True)

def fetch_data():
    global latest_emotion_scores, latest_transformation, last_processed_scores
    emotions_url = "http://127.0.0.1:8010/get_emotion_data"
    transformation_url = "http://127.0.0.1:8010/get_latest_transformation"  # Endpoint to get latest transformation
    last_trigger_time = 0
    min_trigger_interval = 5  # minimum seconds between workflow triggers
    
    while True:
        try:
            # Fetch emotions
            response = requests.get(emotions_url)
            if response.status_code == 200:
                data = response.json()
                new_emotions = data.get("emotions", {})
                current_time = time.time()
                
                if (new_emotions != latest_emotion_scores and 
                    current_time - last_trigger_time >= min_trigger_interval):
                    latest_emotion_scores = new_emotions
                    global_vars.set_emotions(latest_emotion_scores)
                    print("✅ Updated emotion data:", latest_emotion_scores, flush=True)
                    # Trigger workflow when emotions change
                    #trigger_workflow()
                    last_trigger_time = current_time
            else:
                print("⚠️ Emotions API error:", response.status_code, flush=True)
                
            # Fetch transformation
            try:
                trans_response = requests.get(transformation_url)
                if trans_response.status_code == 200:
                    trans_data = trans_response.json()
                    if trans_data:
                        latest_transformation = {
                            "from": trans_data.get("from", "Uncertainty"),
                            "to": trans_data.get("to", "Confidence")
                        }
                        global_vars.set_transformation(latest_transformation)
                        print("✅ Updated transformation data:", latest_transformation, flush=True)
            except Exception as e:
                print(f"⚠️ Failed to fetch transformation: {e}", flush=True)
                # Continue execution even if transformation fetch fails
                
        except Exception as e:
            print("❌ Failed to fetch emotions:", e, flush=True)
            
        time.sleep(3)

# Start the background thread to poll the API
#threading.Thread(target=fetch_data, daemon=True).start()

class EmotionImportNode:
    """
    A ComfyUI node that outputs the latest emotion scores imported from the API as a dictionary.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("DICT",)
    RETURN_NAMES = ("emotion_scores",)
    FUNCTION = "get_emotions"
    CATEGORY = "Custom/Emotions"

    def get_emotions(self):
        return (latest_emotion_scores,)

class TransformationImportNode:
    """
    A ComfyUI node that outputs the latest transformation states imported from the API.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING", "STRING", "DICT")
    RETURN_NAMES = ("from_state", "to_state", "transformation_data")
    FUNCTION = "get_transformation"
    CATEGORY = "Custom/Transformations"

    def get_transformation(self):
        return (latest_transformation.get("from", "Uncertainty"), 
                latest_transformation.get("to", "Confidence"),
                latest_transformation)

NODE_CLASS_MAPPINGS = {
    "Emotion Import": EmotionImportNode,
    "Transformation Import": TransformationImportNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Emotion Import": "Emotion Import Node",
    "Transformation Import": "Transformation Import Node"
}
