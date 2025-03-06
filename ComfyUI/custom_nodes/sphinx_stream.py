import asyncio
from aiohttp import web
from server import PromptServer
from . import global_vars

async def ws_sphinx(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print("ws_sphinx connected")
    
    last_sent = None
    try:
        while True:
            await asyncio.sleep(1)
            if global_vars.latest_image_data is not None and global_vars.latest_image_data != last_sent:
                print("Sending image of size:", len(global_vars.latest_image_data))
                await ws.send_bytes(global_vars.latest_image_data)
                last_sent = global_vars.latest_image_data
            else:
                # Optionally send a ping to keep the connection alive
                await ws.send_str("ping")
    except Exception as e:
        print("Error in ws_sphinx:", e)
    finally:
        await ws.close()
    return ws

# Register the route
@PromptServer.instance.routes.get("/ws_sphinx", allow_head=False)
async def handle_ws_sphinx(request):
    return await ws_sphinx(request)
