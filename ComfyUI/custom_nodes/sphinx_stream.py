import asyncio
from aiohttp import web
from server import PromptServer
import os
import sys
import json
import base64
sys.path.append(os.path.dirname(__file__))
import global_vars

@PromptServer.instance.routes.get("/ws_sphinx")
async def ws_sphinx(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print("ws_sphinx connected")
    
    last_sent = None
    try:
        while True:
            await asyncio.sleep(1)
            # Re-read latest_image_data from global_vars (since it is mutable)
           
            if global_vars.latest_image_data is not None and global_vars.latest_image_data != last_sent:
                # Convert binary image data to base64
                image_base64 = base64.b64encode(global_vars.latest_image_data["image"]).decode('utf-8')
                
                data_to_send = {
                    "image": image_base64,
                    "emotions": global_vars.get_emotions()
                }
                print("Sending image and emotions data")
                await ws.send_str(json.dumps(data_to_send))
                last_sent = global_vars.latest_image_data
            else:
                # Optionally send a ping to keep the connection alive.
                await ws.send_str("ping")
    except Exception as e:
        print("Error in ws_sphinx:", e)
    finally:
        await ws.close()
    return ws

# This empty mapping prevents ComfyUI from trying to load this file as a node.
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

