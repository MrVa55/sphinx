"""
This module stores global variables for sharing data between nodes.
Not a ComfyUI node, just a helper module.
"""

# Global variable to store the latest binary image data (e.g., PNG bytes)
latest_image_data = None

# Explicitly mark what should be imported
__all__ = ['latest_image_data']