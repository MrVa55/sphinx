import websocket
import uuid
import json
import urllib.request
import urllib.parse
import io
from PIL import Image

# --- Configuration ---
server_address = "n3oqe3l8rvw50y-3020.proxy.runpod.net"  # Your Runpod address (without scheme)
client_id = str(uuid.uuid4())
ws_url = f"wss://{server_address}/ws?clientId={client_id}"

# --- Function to queue a prompt via HTTP ---
def queue_prompt(prompt):
    payload = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(payload).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"  # Add a common User-Agent header
    }
    req = urllib.request.Request(f"https://{server_address}/prompt", data=data, headers=headers)
    response = urllib.request.urlopen(req)
    return json.loads(response.read())

# --- Function to collect image data from the WS ---
def get_images(ws, prompt):
    # Queue the prompt that includes the SaveImageWebsocket node
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    current_node = ""
    
    # Listen on the WS until execution is complete.
    while True:
        message = ws.recv()
        # Status messages (text) tell you which node is executing.
        if isinstance(message, str):
            msg_json = json.loads(message)
            if msg_json.get("type") == "executing":
                data = msg_json.get("data", {})
                if data.get("prompt_id") == prompt_id:
                    if data.get("node") is None:
                        # Execution finished.
                        break
                    else:
                        current_node = data.get("node")
        else:
            # When a binary message is received from the SaveImageWebsocket node,
            # capture it (slicing off header bytes if necessary).
            if current_node == "save_image_websocket_node":
                output_images.setdefault(current_node, []).append(message[8:])
    return output_images

# --- Define a minimal prompt (node graph) ---
# Make sure this prompt contains the SaveImageWebsocket node.
prompt = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8,
            "denoise": 1,
            "latent_image": ["5", 0],
            "model": ["4", 0],
            "negative": ["7", 0],
            "positive": ["6", 0],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 5,
            "steps": 20
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {"batch_size": 1, "height": 512, "width": 512}
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {"clip": ["4", 1], "text": "masterpiece best quality man"}
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {"clip": ["4", 1], "text": "bad hands"}
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
    },
    "save_image_websocket_node": {
        "class_type": "SaveImageWebsocket",
        "inputs": {"images": ["8", 0]}
    }
}

# --- Main Client Code ---
print("Connecting to:", ws_url)
ws = websocket.create_connection(ws_url)
print("Connected!")

# This will queue the prompt and wait for the SaveImageWebsocket node to output image data.
images = get_images(ws, prompt)
ws.close()

# Process and display the image(s)
for node_id, image_list in images.items():
    for img_data in image_list:
        try:
            image = Image.open(io.BytesIO(img_data))
            image.show()
        except Exception as e:
            print("Error processing image:", e)
