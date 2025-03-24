import json
import requests
import os
import time
import random
import threading
import uuid

def load_workflow(workflow_path=None):
    """
    Loads the workflow JSON from the specified path or the default location.
    """
    if workflow_path is None:
        # Try multiple possible locations
        possible_paths = [
            "/workspace/app/workflow.json",  # Primary location in workspace
            "/ComfyUI/custom_nodes/workflow.json",  # ComfyUI custom nodes location
            "/sphinxfiles/app/workflow.json"  # Original image location
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                workflow_path = path
                print(f"Found workflow at: {path}")
                break
        else:
            raise FileNotFoundError("Could not find workflow.json in any expected location")
    
    print(f"Loading workflow from: {workflow_path}")
    with open(workflow_path, 'r') as f:
        return json.load(f)

def get_comfyui_url():
    """Get the appropriate ComfyUI URL based on the environment"""
    # Check if we're running in RunPod
    pod_id = os.environ.get('RUNPOD_POD_ID')
    
    if pod_id:
        # We're in RunPod, construct the internal URL
        # For services within the same container, we can use localhost
        return "http://127.0.0.1:3020"
    else:
        # Default for local development
        return "http://127.0.0.1:3020"

def trigger_workflow(comfyui_url="http://127.0.0.1:3020", workflow_data=None, emotion_prompts=None, base_prompt=None):
    """
    Triggers the ComfyUI workflow using the API format.
    """
    try:
        if workflow_data is None:
            workflow_data = load_workflow()

        print(f"ComfyUI health check status: 200")  # We know it's working from the minimal test
        print(f"Converting workflow to API format...")

        # Create a new API-format workflow based on our existing workflow
        api_workflow = {}
        
        # First, find each node by its ID and convert it to API format
        for node in workflow_data["nodes"]:
            node_id = str(node["id"])
            node_type = node["type"]
            
            # Create the basic node structure
            api_node = {
                "class_type": node_type,
                "inputs": {}
            }
            
            # Add widget values if they exist
            if "widgets_values" in node:
                # The order matters for widgets, so we need to handle this carefully
                if node_type == "KSampler":
                    # Update seed for KSampler
                    api_node["inputs"]["seed"] = int(time.time()) % 1000000000
                    api_node["inputs"]["steps"] = node["widgets_values"][2]
                    api_node["inputs"]["cfg"] = node["widgets_values"][3]
                    api_node["inputs"]["sampler_name"] = node["widgets_values"][4]
                    api_node["inputs"]["scheduler"] = node["widgets_values"][5]
                    api_node["inputs"]["denoise"] = node["widgets_values"][6]
                elif node_type == "EmptyLatentImage":
                    api_node["inputs"]["width"] = node["widgets_values"][0]
                    api_node["inputs"]["height"] = node["widgets_values"][1]
                    api_node["inputs"]["batch_size"] = node["widgets_values"][2]
                elif node_type == "CLIPTextEncode":
                    api_node["inputs"]["text"] = node["widgets_values"][0]
                elif node_type == "CheckpointLoaderSimple":
                    api_node["inputs"]["ckpt_name"] = node["widgets_values"][0]
                elif node_type == "SaveImage":
                    api_node["inputs"]["filename_prefix"] = node["widgets_values"][0]
                elif node_type == "CombineEmotionPromptsNode":
                    # Add base prompt if provided
                    if base_prompt:
                        api_node["inputs"]["base_prompt"] = base_prompt
                    else:
                        api_node["inputs"]["base_prompt"] = node["widgets_values"][0] if node["widgets_values"] else ""
                elif node_type == "EmotionsPromptsInputNode":
                    # Handle emotion prompts
                    emotion_keys = [
                        "admiration", "amusement", "anger", "annoyance", "approval", "caring", 
                        "confusion", "curiosity", "desire", "disappointment", "disapproval", 
                        "disgust", "embarrassment", "excitement", "fear", "gratitude", 
                        "grief", "joy", "love", "nervousness", "optimism", "pride", 
                        "realization", "relief", "remorse", "sadness", "surprise", "neutral"
                    ]
                    for i, key in enumerate(emotion_keys):
                        if i < len(node["widgets_values"]):
                            api_node["inputs"][key] = node["widgets_values"][i]
            
            # Add to our API workflow
            api_workflow[node_id] = api_node
        
        # Now process all the connections between nodes
        for link in workflow_data["links"]:
            # Format is [link_id, from_node, from_slot, to_node, to_slot, data_type]
            from_node = str(link[1])
            to_node = str(link[3])
            to_slot = str(link[4])
            
            # Find the corresponding node
            to_node_data = next((n for n in workflow_data["nodes"] if n["id"] == link[3]), None)
            if to_node_data:
                input_name = None
                # Find the input name based on the slot index
                for input_data in to_node_data.get("inputs", []):
                    if input_data.get("slot_index") == link[4]:
                        input_name = input_data.get("name")
                        break
                
                if input_name and to_node in api_workflow:
                    api_workflow[to_node]["inputs"][input_name.lower()] = [from_node, link[2]]
        
        # Prepare the data for ComfyUI's API
        prompt_data = {
            "prompt": api_workflow
        }

        print(f"Sending API-format workflow to ComfyUI: {comfyui_url}")
        
        # Send to ComfyUI
        try:
            response = requests.post(
                f'{comfyui_url}/prompt', 
                json=prompt_data,
                headers={'Content-Type': 'application/json'},
                timeout=30  # Longer timeout for complex workflows
            )
            
            print(f"ComfyUI response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error response from ComfyUI: {response.status_code}")
                print(f"Response content: {response.text}")
            else:
                print("Successfully sent workflow to ComfyUI")
                try:
                    print(f"Response content: {response.text[:500]}...")
                except:
                    pass
            
            return response
            
        except requests.exceptions.Timeout:
            print(f"⚠️ Request to ComfyUI timed out after 30 seconds")
            resp = requests.Response()
            resp.status_code = 504
            return resp
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error making request to ComfyUI: {e}")
            resp = requests.Response()
            resp.status_code = 500
            return resp
            
    except Exception as e:
        print(f"❌ Unexpected error in trigger_workflow: {e}")
        import traceback
        traceback.print_exc()
        resp = requests.Response()
        resp.status_code = 500
        return resp

def test_minimal_workflow(comfyui_url="http://127.0.0.1:3020"):
    """
    Test with an extremely minimal workflow to check if ComfyUI is responding properly.
    """
    # This is a minimal stable diffusion workflow
    minimal_workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "sd_xl_base_1.0.safetensors"
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "height": 512,
                "width": 512
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "a beautiful landscape"
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "text, watermark"
            }
        },
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
                "seed": int(time.time()) % 1000000000,
                "steps": 20
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "ComfyUI_test",
                "images": ["8", 0]
            }
        }
    }
    
    # Prepare the data for ComfyUI's API
    prompt_data = {
        "prompt": minimal_workflow
    }
    
    print("Testing with minimal workflow...")
    try:
        # Make sure we're using the correct API endpoint
        api_endpoint = f"{comfyui_url}/prompt"
        
        # For https URLs (like the RunPod proxy), we need to handle this differently
        if comfyui_url.startswith("https"):
            # Try alternate endpoint pattern for proxy
            api_endpoint = f"{comfyui_url}/api/prompt"
            print(f"Using HTTPS proxy endpoint: {api_endpoint}")
        
        print(f"Sending to API endpoint: {api_endpoint}")
        response = requests.post(
            api_endpoint, 
            json=prompt_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        # If we got a 405, try the alternate endpoint
        if response.status_code == 405 and not api_endpoint.endswith("/api/prompt"):
            alt_endpoint = f"{comfyui_url}/api/prompt"
            print(f"Got 405, trying alternate endpoint: {alt_endpoint}")
            response = requests.post(
                alt_endpoint, 
                json=prompt_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            print(f"Alternate endpoint response status: {response.status_code}")
            print(f"Alternate endpoint response text: {response.text}")
        
        return response
    except Exception as e:
        print(f"Error testing minimal workflow: {e}")
        return None

def validate_workflow(workflow_data):
    """
    Check for common issues in the workflow data that might cause ComfyUI errors.
    """
    issues = []
    
    # Check if required top-level keys exist
    required_keys = ["nodes", "links"]
    for key in required_keys:
        if key not in workflow_data:
            issues.append(f"Missing required key: {key}")
    
    # Check if all nodes have the required fields
    for i, node in enumerate(workflow_data.get("nodes", [])):
        if "id" not in node:
            issues.append(f"Node at index {i} is missing 'id' field")
        if "type" not in node:
            issues.append(f"Node at index {i} is missing 'type' field")
    
    # Check if all links reference valid nodes
    node_ids = set(node.get("id") for node in workflow_data.get("nodes", []))
    for i, link in enumerate(workflow_data.get("links", [])):
        if len(link) < 2:
            issues.append(f"Link at index {i} has invalid format")
            continue
        source_id = link[0]
        target_id = link[2]
        if source_id not in node_ids:
            issues.append(f"Link at index {i} references non-existent source node: {source_id}")
        if target_id not in node_ids:
            issues.append(f"Link at index {i} references non-existent target node: {target_id}")
    
    return issues

def test_comfyui_connection():
    """
    Test connection to ComfyUI and determine the best URL to use.
    Returns the URL that works.
    """
    possible_urls = [
        "http://127.0.0.1:3020",
        "http://localhost:3020", 
        "http://comfyui:3020"
    ]
    
    for url in possible_urls:
        try:
            print(f"Testing connection to ComfyUI at: {url}")
            response = requests.get(f"{url}/system_stats", timeout=2)
            if response.status_code == 200:
                print(f"✅ Successfully connected to ComfyUI API at {url}")
                return url
        except Exception as e:
            print(f"Could not connect to {url}: {e}")
    
    # If nothing else works, use the default URL
    print("⚠️ No ComfyUI connection verified, using default URL")
    return "http://127.0.0.1:3020"

def trigger_workflow_simple(comfyui_url="http://127.0.0.1:3020"):
    """
    Triggers a simple workflow with a direct text prompt.
    """
    try:
        # Create a minimal workflow
        workflow = {
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                }
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "batch_size": 1,
                    "height": 512,
                    "width": 512
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": emotion_prompt
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": "ugly, blurry, low quality"
                }
            },
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
                    "seed": int(time.time()) % 1000000000,
                    "steps": 20
                }
            }
        }
        
        # Prepare the data for ComfyUI's API
        prompt_data = {
            "prompt": workflow
        }
        
        print(f"Sending simplified workflow to ComfyUI with emotion prompt: {emotion_prompt}")
        
        # Send to ComfyUI
        response = requests.post(
            f'{comfyui_url}/prompt', 
            json=prompt_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"ComfyUI response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response content: {response.text}")
        else:
            print("Successfully sent workflow to ComfyUI!")
            try:
                response_data = response.json()
                print(f"Prompt ID: {response_data.get('prompt_id')}")
                print(f"Number: {response_data.get('number')}")
            except:
                pass
        
        return response
        
    except Exception as e:
        print(f"Error in trigger_workflow_simple: {e}")
        import traceback
        traceback.print_exc()
        resp = requests.Response()
        resp.status_code = 500
        return resp

def run_standard_workflow_with_emotions(comfyui_url):
    """
    Run a standard workflow that uses built-in nodes but incorporates the emotion data.
    This doesn't require custom nodes to be installed.
    """
    def background_task():
        try:
            # Use a fixed client ID
            client_id = "sphinx_api_client"
            print(f"[Background] Using fixed client ID: {client_id}")
            
            # First get the emotions from our API
            try:
                print(f"[Background] Requesting emotions from API at http://127.0.0.1:8010/get_emotion_data")
                emotions_response = requests.get("http://127.0.0.1:8010/get_emotion_data", timeout=5)  # Increase timeout
                print(f"[Background] Emotion API response status: {emotions_response.status_code}")
                
                if emotions_response.status_code == 200:
                    emotions_data = emotions_response.json()
                    emotions = emotions_data.get("emotions", {})
                    print(f"[Background] Got emotions: {emotions}")
                    
                    # Sort emotions by score (highest first)
                    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
                    top_emotions = sorted_emotions[:3]  # Get top 3 emotions
                    print(f"[Background] Top emotions: {top_emotions}")
                    
                    # Create a prompt based on the top emotions
                    if top_emotions:
                        emotion_prompt = "A scene showing "
                        for i, (emotion, score) in enumerate(top_emotions):
                            if i > 0:
                                emotion_prompt += " and " if i == len(top_emotions) - 1 else ", "
                            emotion_prompt += f"{emotion}"
                        
                        # Add some visual flair based on emotions
                        if "joy" in dict(top_emotions) or "excitement" in dict(top_emotions):
                            emotion_prompt += ", bright colors, sunshine"
                        if "sadness" in dict(top_emotions) or "grief" in dict(top_emotions):
                            emotion_prompt += ", dark tones, rain"
                        if "anger" in dict(top_emotions):
                            emotion_prompt += ", intense red tones"
                        if "fear" in dict(top_emotions):
                            emotion_prompt += ", shadows, mist"
                            
                        emotion_prompt += ", high quality, detailed, beautiful composition"
                        
                        print(f"[Background] Generated emotion prompt: {emotion_prompt}")
                    else:
                        emotion_prompt = "A beautiful landscape, high quality"
                        print(f"[Background] Using default prompt (no top emotions): {emotion_prompt}")
                else:
                    emotion_prompt = "A beautiful landscape, high quality"
                    print(f"[Background] Using default prompt (API error): {emotion_prompt}")
            except Exception as e:
                print(f"[Background] Error getting emotions: {e}")
                emotion_prompt = "A beautiful landscape, high quality"
                print(f"[Background] Using default prompt (exception): {emotion_prompt}")
            
            print(f"[Background] Building workflow with prompt: {emotion_prompt}")
            
            # Set up a workflow using standard nodes
            workflow = {
                "4": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {
                        "ckpt_name": "sd_xl_base_1.0.safetensors"
                    }
                },
                "5": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {
                        "width": 768,  # Larger image
                        "height": 768,
                        "batch_size": 1
                    }
                },
                "6": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "clip": ["4", 1],
                        "text": emotion_prompt  # Use our emotion-based prompt
                    }
                },
                "7": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "clip": ["4", 1],
                        "text": "ugly, blurry, low quality, distorted"
                    }
                },
                "3": {
                    "class_type": "KSampler",
                    "inputs": {
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0],
                        "seed": int(time.time()) % 1000000000,
                        "steps": 30,  # More steps
                        "cfg": 8,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": 1
                    }
                },
                "8": {
                    "class_type": "VAEDecode",
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    }
                },
                "9": {
                    "class_type": "SaveImage",
                    "inputs": {
                        "images": ["8", 0],
                        "filename_prefix": "ComfyUI_emotion"
                    }
                },
                "13": {
                    "class_type": "SaveImageWebsocket",
                    "inputs": {
                        "images": ["8", 0]
                    }
                }
            }
            
            # Prepare the prompt
            prompt = {
                "prompt": workflow,
                "client_id": client_id
            }
            
            # Queue the prompt
            print(f"[Background] Sending workflow to ComfyUI: {comfyui_url}/prompt")
            print(f"[Background] Full request details: URL={comfyui_url}/prompt, ClientID={client_id}")
            
            # Add the Content-Type header which might be required
            response = requests.post(
                f"{comfyui_url}/prompt", 
                json=prompt,
                headers={'Content-Type': 'application/json'},
                timeout=30  # Longer timeout
            )
            
            print(f"[Background] ComfyUI response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    prompt_id = response_data.get('prompt_id')
                    print(f"[Background] Success! Prompt ID: {prompt_id}")
                    
                    # Save the client ID and prompt ID
                    with open("/workspace/app/last_prompt.json", "w") as f:
                        json.dump({
                            "client_id": client_id,
                            "prompt_id": prompt_id,
                            "timestamp": time.time()
                        }, f)
                    print(f"[Background] Saved prompt info to file")
                except Exception as e:
                    print(f"[Background] Error processing response: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[Background] Error from ComfyUI: {response.status_code}")
                print(f"[Background] Response text: {response.text}")
                
        except Exception as e:
            print(f"[Background] Critical error in background workflow: {e}")
            import traceback
            traceback.print_exc()
    
    # Start the background thread
    print("[Main] Creating background thread for workflow execution")
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()
    print("[Main] Background thread started")
    
    return thread

def get_available_custom_nodes(comfyui_url):
    """
    Query ComfyUI for available nodes to find correct custom node names
    """
    print("[DEBUG] Checking available custom nodes in ComfyUI...")
    try:
        response = requests.get(f"{comfyui_url}/object_info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Look for emotion-related nodes
            emotion_nodes = []
            for node_name in data.get("object_info", {}).keys():
                if "emotion" in node_name.lower() or "prompt" in node_name.lower():
                    emotion_nodes.append(node_name)
                    print(f"[DEBUG] Found potential emotion node: {node_name}")
            
            return emotion_nodes
        else:
            print(f"[DEBUG] Error getting node info: {response.status_code}")
            return []
    except Exception as e:
        print(f"[DEBUG] Error checking node info: {e}")
        return []

def run_workflow_with_custom_nodes(comfyui_url):
    """
    Run the workflow with the correct custom node names and required inputs.
    """
    def background_task():
        try:
            client_id = "sphinx_api_client"
            print(f"[WORKFLOW] Starting custom workflow execution...")
            
            # Use the EXACT node names from the source files
            emotion_import_node = "Emotion Import"
            emotions_prompts_node = "EmotionsPromptsInputNode"  
            combine_node = "CombineEmotionPromptsNode"
            
            # Get the current timestamp for a unique seed
            seed = int(time.time()) % 1000000000
            
            # Create a dictionary of visual prompts for each emotion
            emotion_visual_prompts = {
                "admiration": "golden light streaming through mist, upward flowing forms, ethereal atmosphere, reverent glow",
                "amusement": "playful swirls of bright colors, light airy textures, bubbling patterns, whimsical flows",
                "anger": "sharp jagged lines, intense red and black patterns, fierce energy, explosive textures, burning energy",
                "annoyance": "irritating textures, prickly patterns, chaotic small disturbances, subtle discord",
                "approval": "harmonious balance, warm golden tones, upward curves, gentle affirmative flows",
                "caring": "soft protective curves, nurturing warm light, gentle enveloping forms, nestled shapes",
                "confusion": "intersecting twisted paths, foggy perception, labyrinthine patterns, disoriented perspective",
                "curiosity": "spiraling inquisitive patterns, doors slightly ajar, mysterious partial reveals, beckoning paths",
                "desire": "reaching tendrils of color, yearning flows, passionate red undertones, magnetic attraction",
                "disappointment": "downward flows, deflated forms, muted grays and blues, abandoned hopes",
                "disapproval": "stark contrasts, harsh lines crossing, barriers, cold colors, rejecting shapes",
                "disgust": "repulsive textures, sickly green hues, corrupted forms, nauseating swirls", 
                "embarrassment": "flushed pink hues, hiding curves, avoidant patterns, exposed vulnerability",
                "excitement": "explosive bursts of color, dynamic upward movement, vibrant energy, electrical sparks",
                "fear": "dark negative spaces, looming shadows, claustrophobic textures, threatening shapes",
                "gratitude": "opening expansive forms, warm gentle light, peaceful flowing lines, harmonious connections",
                "grief": "heavy dark flows, tears of blue, weighty textures, emptiness within form, profound depth",
                "joy": "radiant light bursts, uplifting colors, expansive energy, dancing rhythm, celebration",
                "love": "intertwining forms, soft pink glow, passionate red undertones, heart-like curves, warm embrace",
                "nervousness": "jittery lines, unstable patterns, scattered energy, trembling textures, anticipation",
                "optimism": "rising sun-like forms, hopeful light breaking through, upward trajectory, brightening horizon",
                "pride": "tall vertical forms, rich colors, expansive presence, dignified composition, achievement",
                "realization": "bursting insight, illuminated patterns, clarity emerging from chaos, epiphany light",
                "relief": "tension releasing into flow, burdens lifting, smooth transitions, spacious breathing room",
                "remorse": "heavy downward forms, dark reflective surfaces, sorrowful blue depths, shadows of regret",
                "sadness": "flowing tears of blue, heavy weight pulling down, lonely isolated forms, gentle melancholy",
                "surprise": "sudden explosive patterns, unexpected breaks in rhythm, startled compositions, revelation"
            }
            
            # Set up workflow with the correct node names AND required inputs
            workflow = {
                "4": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {
                        "ckpt_name": "sd_xl_base_1.0.safetensors"
                    }
                },
                "5": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {
                        "width": 768,
                        "height": 768,
                        "batch_size": 1
                    }
                },
                "7": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "clip": ["4", 1],
                        "text": "ugly, blurry, low quality, distorted"
                    }
                },
                "3": {
                    "class_type": "KSampler",
                    "inputs": {
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0],
                        "seed": seed,
                        "steps": 20,
                        "cfg": 8,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": 1
                    }
                },
                "8": {
                    "class_type": "VAEDecode",
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    }
                },
                "9": {
                    "class_type": "SaveImage",
                    "inputs": {
                        "images": ["8", 0],
                        "filename_prefix": "ComfyUI_emotion"
                    }
                },
                "13": {
                    "class_type": "SaveImageWebsocket",
                    "inputs": {
                        "images": ["8", 0]
                    }
                },
                # Custom emotion node with no required inputs
                "10": {
                    "class_type": emotion_import_node,
                    "inputs": {}
                },
                # EmotionsPromptsInputNode with visual prompts for each emotion
                "12": {
                    "class_type": emotions_prompts_node,
                    "inputs": emotion_visual_prompts
                },
                # CombineEmotionPromptsNode with required inputs
                "11": {
                    "class_type": combine_node,
                    "inputs": {
                        "emotion_scores": ["10", 0],
                        "emotion_prompts": ["12", 0],
                        "base_prompt": "A detailed, high-quality artistic scene with"
                    }
                },
                "6": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "clip": ["4", 1],
                        "text": ["11", 0]
                    }
                }
            }
            
            prompt = {
                "prompt": workflow,
                "client_id": client_id
            }
            
            # Send the workflow to ComfyUI
            print(f"[WORKFLOW] Sending request to {comfyui_url}/prompt")
            response = requests.post(
                f"{comfyui_url}/prompt", 
                json=prompt,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"[WORKFLOW] Response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                prompt_id = response_data.get('prompt_id')
                print(f"[WORKFLOW] Success! Prompt ID: {prompt_id}")
                
                with open("/workspace/app/last_prompt.json", "w") as f:
                    json.dump({
                        "client_id": client_id,
                        "prompt_id": prompt_id,
                        "timestamp": time.time()
                    }, f)
            else:
                print(f"[WORKFLOW] Error: {response.status_code}")
                error_text = response.text
                print(f"[WORKFLOW] Response text: {error_text}")
                
        except Exception as e:
            print(f"[WORKFLOW] Error in background task: {e}")
            import traceback
            traceback.print_exc()
    
    # Start the background thread
    print("[MAIN] Creating background thread for workflow execution")
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()
    print("[MAIN] Thread started successfully")
    
    return thread