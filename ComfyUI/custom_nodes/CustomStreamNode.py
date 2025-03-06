# CustomStreamNode.py

import os
import io
import numpy as np
from PIL import Image
import importlib.util
from . import global_vars  # Import from the same directory

def import_sphinx_stream():
    """Import sphinx_stream module from the same directory"""
    try:
        # Get the path to sphinx_stream.py in the same directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sphinx_stream_path = os.path.join(current_dir, "sphinx_stream.py")
        
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("sphinx_stream", sphinx_stream_path)
        sphinx_stream = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sphinx_stream)
        return sphinx_stream
    except Exception as e:
        print(f"Error importing sphinx_stream: {e}")
        return None

def convert_tensor_to_pil(image):
    """
    Convert an image tensor/NumPy array to a PIL Image.
    This function prints the shape for debugging and attempts to remove
    any extra dimensions so that the final image is in (H, W, C) format.
    """
    # If image is a tensor, convert it to a NumPy array.
    if hasattr(image, "cpu"):
        image = image.cpu().detach().numpy()
    
    print("CustomStreamNode received image shape:", image.shape)
    
    # If image has 4 dimensions (e.g. [batch, channels, height, width]), remove the batch.
    if image.ndim == 4:
        image = image[0]
        print("After removing batch, shape:", image.shape)
    
    # At this point, image is expected to be 3D.
    if image.ndim == 3:
        # If the first dimension is small (e.g. 1, 3, or 4), assume it's channels.
        if image.shape[0] in [1, 3, 4]:
            image = np.transpose(image, (1, 2, 0))
            print("After transposing from channel-first to channel-last, shape:", image.shape)
    else:
        print("Unexpected image dimensions:", image.shape)
    
    # Squeeze any extra singleton dimensions.
    image = np.squeeze(image)
    print("After squeeze, final shape:", image.shape)
    
    # If image is grayscale (2D), convert to 3-channel RGB.
    if image.ndim == 2:
        image = np.stack([image]*3, axis=-1)
        print("Converted grayscale to RGB, shape:", image.shape)
    
    # If the image is not uint8 and is in [0,1] range, scale to [0,255].
    if image.dtype != np.uint8:
        image = (np.clip(image, 0, 1) * 255).astype(np.uint8)
    
    return Image.fromarray(image)

class CustomStreamNode:
    """
    This node intercepts the image output (from a VAE decode, for example), converts it
    to PNG bytes for streaming via a custom WebSocket endpoint, and passes the original
    image output unchanged to downstream nodes (such as SaveImage).
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",)}}
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_image"
    CATEGORY = "Custom"
    
    def process_image(self, image):
        # Convert the incoming image to a PIL Image if it's not already one.
        try:
            if isinstance(image, Image.Image):
                pil_image = image
            else:
                pil_image = convert_tensor_to_pil(image)
        except Exception as e:
            raise ValueError(f"Conversion to PIL failed: {e}")
        
        # Convert the PIL image to PNG bytes using an in-memory buffer.
        output_buffer = io.BytesIO()
        pil_image.save(output_buffer, format="PNG")
        binary_data = output_buffer.getvalue()
        
        # Update the global variable
        global_vars.latest_image_data = binary_data
        print("CustomStreamNode updated latest_image_data with", len(binary_data), "bytes")
        
        return (image,)

NODE_CLASS_MAPPINGS = {
    "CustomStreamNode": CustomStreamNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomStreamNode": "Custom Stream Node"
}
