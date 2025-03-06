import websocket
import io
from PIL import Image

# Replace with your actual Runpod domain (without scheme)
server_address = "n3oqe3l8rvw50y-3020.proxy.runpod.net"
ws_url = f"wss://{server_address}/ws_sphinx"

print("Connecting to:", ws_url)
ws = websocket.create_connection(ws_url)
print("Connected!")

while True:
    try:
        msg = ws.recv()
    except Exception as e:
        print("Error receiving message:", e)
        break

    # Check if the message is a text message (like "ping")
    if isinstance(msg, str):
        print("Received a text message:", msg)
        # Ignore ping messages and continue looping.
        if msg.strip().lower() == "ping":
            continue
    elif isinstance(msg, bytes):
        try:
            image = Image.open(io.BytesIO(msg))
            image.show()  # Display the image using your default image viewer.
            print("Image received and displayed, length:", len(msg))
        except Exception as e:
            print("Error processing image:", e)
    else:
        print("Received message of unknown type:", type(msg))

ws.close()
