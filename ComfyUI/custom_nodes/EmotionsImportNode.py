import requests
import time
import threading

# Global variable to store emotion scores (updated in the background)
latest_emotion_scores = {}

def fetch_emotions():
    global latest_emotion_scores
    api_url = "http://127.0.0.1:8010/get_emotion_data"
    while True:
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                # Assume data["emotions"] is a dictionary with emotion: confidence pairs.
                latest_emotion_scores = data.get("emotions", {})
                print("✅ Updated emotion data:", latest_emotion_scores, flush=True)
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
        print(f"📢 EmotionImportNode executing with data: {latest_emotion_scores}", flush=True)
        print(f"📢 Type of data being returned: {type(latest_emotion_scores)}", flush=True)
        return (latest_emotion_scores,)

    @classmethod
    def IS_CHANGED(cls):
        # Return current time to ensure the node is always marked as changed.
        return time.time()

NODE_CLASS_MAPPINGS = {
    "Emotion Import": EmotionImportNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Emotion Import": "Emotion Import Node"
}
