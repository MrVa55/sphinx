# global_vars.py

# Global variables module for ComfyUI custom nodes
# This allows sharing data between nodes and threads

# Global variables for emotions and transformations
emotions = {}
transformation = {"from": "Uncertainty", "to": "Confidence"}

def set_emotions(emotion_data):
    """Set the global emotions dictionary"""
    global emotions
    emotions = emotion_data

def get_emotions():
    """Get the global emotions dictionary"""
    global emotions
    return emotions

def set_transformation(trans_data):
    """Set the global transformation dictionary"""
    global transformation
    transformation = trans_data

def get_transformation():
    """Get the global transformation dictionary"""
    global transformation
    return transformation

# This empty mapping prevents ComfyUI from trying to load this file as a node.
NODE_CLASS_MAPPINGS = {}
