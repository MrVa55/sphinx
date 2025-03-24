import json
import requests
import os
import time
import random
import threading
import uuid

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