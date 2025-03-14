import os
import sys
sys.path.append(os.path.dirname(__file__))

import io
import numpy as np
from PIL import Image
import global_vars  # Import the shared global variable module

def convert_tensor_to_pil(image):
    """
    Convert an image tensor/NumPy array to a PIL Image.
    This function prints the shape for debugging and attempts to remove
    any extra dimensions so that the final image is in (H, W, C) format.
    """
    if hasattr(image, "cpu"):
        image = image.cpu().detach().numpy()
    
    print("CustomStreamNode received image shape:", image.shape)
    
    if image.ndim == 4:
        image = image[0]
        print("After removing batch, shape:", image.shape)
    
    if image.ndim == 3 and image.shape[0] in [1, 3, 4]:
        image = np.transpose(image, (1, 2, 0))
        print("After transposing, shape:", image.shape)
    
    image = np.squeeze(image)
    print("After squeeze, final shape:", image.shape)
    
    if image.ndim == 2:
        image = np.stack([image]*3, axis=-1)
        print("Converted grayscale to RGB, shape:", image.shape)
    
    if image.dtype != np.uint8:
        image = (np.clip(image, 0, 1) * 255).astype(np.uint8)
    
    return Image.fromarray(image)

class CustomStreamNode:
    """
    This node intercepts the image output, converts it to PNG bytes for streaming,
    updates the shared global variable (latest_image_data in global_vars), and passes
    the original image along to downstream nodes.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE",)}}
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_image"
    CATEGORY = "Custom"
    
    def process_image(self, image):
        try:
            if isinstance(image, Image.Image):
                pil_image = image
            else:
                pil_image = convert_tensor_to_pil(image)
        except Exception as e:
            raise ValueError(f"Conversion to PIL failed: {e}")
        
        output_buffer = io.BytesIO()
        pil_image.save(output_buffer, format="PNG")
        binary_data = output_buffer.getvalue()
        
        # Update the global variable.
        global_vars.latest_image_data = binary_data
        print("CustomStreamNode updated latest_image_data with", len(binary_data), "bytes")
        
        return (image,)

NODE_CLASS_MAPPINGS = {
    "CustomStreamNode": CustomStreamNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomStreamNode": "Custom Stream Node"
}
