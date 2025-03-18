# global_vars.py

latest_image_data = None
latest_emotions_data = None

def set_emotions(emotions):
    global latest_emotions_data
    latest_emotions_data = emotions

def get_emotions():
    global latest_emotions_data
    return latest_emotions_data

# This empty mapping prevents ComfyUI from trying to load this file as a node.
NODE_CLASS_MAPPINGS = {}
