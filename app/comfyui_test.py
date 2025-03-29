import requests
import os
import json

def test_comfyui_connection():
    """Test if ComfyUI is running and responding to API requests"""
    try:
        print("Testing ComfyUI connection...")
        
        # Try different possible URLs
        urls = [
            "http://127.0.0.1:3020",
            "http://localhost:3020",
            "http://comfyui:3020"
        ]
        
        working_url = None
        
        for url in urls:
            try:
                print(f"Testing URL: {url}")
                response = requests.get(f"{url}/system_stats", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Successfully connected to ComfyUI at {url}")
                    system_stats = response.json()
                    print(f"System stats: {json.dumps(system_stats, indent=2)}")
                    working_url = url
                    break
                else:
                    print(f"❌ Connection failed with status code: {response.status_code}")
            except Exception as e:
                print(f"❌ Error connecting to {url}: {e}")
                
        if not working_url:
            print("❌ Could not connect to ComfyUI API")
            return False
            
        # Try to access the history endpoint
        try:
            print(f"Testing history endpoint at {working_url}/history")
            response = requests.get(f"{working_url}/history")
            if response.status_code == 200:
                history = response.json()
                history_count = len(history.keys())
                print(f"✅ History endpoint working. Found {history_count} entries")
            else:
                print(f"❌ History endpoint failed with status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error accessing history endpoint: {e}")
        
        return working_url
    except Exception as e:
        print(f"❌ Error testing ComfyUI connection: {e}")
        return False

if __name__ == "__main__":
    test_comfyui_connection() 