import requests
import time
import threading
import global_vars
import json
import os

# Global variables
latest_emotion_scores = {}
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

def fetch_emotions():
    global latest_emotion_scores, last_processed_scores
    api_url = "http://127.0.0.1:8010/get_emotion_data"
    last_trigger_time = 0
    min_trigger_interval = 5  # minimum seconds between workflow triggers
    
    while True:
        try:
            response = requests.get(api_url)
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
                    trigger_workflow()
                    last_trigger_time = current_time
            else:
                print("⚠️ API error:", response.status_code, flush=True)
        except Exception as e:
            print("❌ Failed to fetch emotions:", e, flush=True)
        time.sleep(3)

# Start the background thread to poll the API
threading.Thread(target=fetch_emotions, daemon=True).start()

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

NODE_CLASS_MAPPINGS = {
    "Emotion Import": EmotionImportNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Emotion Import": "Emotion Import Node"
}
