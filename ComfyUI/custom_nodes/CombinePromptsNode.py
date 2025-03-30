# CombinePromptsNode.py
import requests

# Transformation prompts dictionary mapping from transformation keywords to prompt suggestions
TRANSFORMATION_PROMPTS = {
    "Closed off": {
        "transformation_to": "Open",
        "prompts": [
            {
                "title": "The Tightly Shut Flower & The Radiant Bloom",
                "from_prompt": "A flower bud remains tightly shut.",
                "to_prompt": "Sunlight warms the flower bud, and it gently unfolds, revealing radiant petals."
            },
            {
                "title": "The Shut Book & The Illuminated Pages",
                "from_prompt": "A book remains shut on a dusty shelf.",
                "to_prompt": "A hand opens the book, revealing glowing pages that invite exploration."
            }
        ]
    },
    "Stagnant": {
        "transformation_to": "Creative",
        "prompts": [
            {
                "title": "The Closed Book & The Rising Phoenix",
                "from_prompt": "A dust-covered book sits opened.",
                "to_prompt": "The dust-covered book bursts into light, and a phoenix rises from it, soaring into the sky."
            },
            {
                "title": "The Still Pond & The Bursting Fountain",
                "from_prompt": "A small, motionless pond sits in a gray, lifeless garden.",
                "to_prompt": "Ripples form on the small, motionless pond, and it rises, bursting into a vibrant, flowing fountain."
            }
        ]
    },
    "Fearful": {
        "transformation_to": "Trusting",
        "prompts": [
            {
                "title": "The Quivering Deer & The Open Meadow",
                "from_prompt": "A small deer stands frozen in a dark forest.",
                "to_prompt": "Sunlight breaks through the forest, and the small deer steps into an open meadow."
            },
            {
                "title": "The Fragile Egg & The Strong Wings",
                "from_prompt": "A delicate egg rests in a nest, unmoving.",
                "to_prompt": "A baby bird emerges from the delicate egg, stretching its wings and taking its first flight."
            }
        ]
    },
    "Hiding": {
        "transformation_to": "Visible",
        "prompts": [
            {
                "title": "The Closed Oyster & The Radiant Pearl",
                "from_prompt": "A pearl remains hidden inside a closed oyster shell.",
                "to_prompt": "The closed oyster shell opens, revealing the pearl shimmering in the light."
            },
            {
                "title": "The Covered Moon & The Lunar Glow",
                "from_prompt": "Clouds obscure the full moon.",
                "to_prompt": "The wind shifts, and the clouds part, revealing the full moon in full brilliance."
            }
        ]
    },
    "Uncentered": {
        "transformation_to": "Centered",
        "prompts": [
            {
                "title": "The Wobbly Top & The Steady Balance",
                "from_prompt": "A spinning top wobbles, very unstable.",
                "to_prompt": "The spinning top steadies, finds its rhythm, and spins in perfect balance."
            }
        ]
    },
    "Silenced": {
        "transformation_to": "Honest",
        "prompts": [
            {
                "title": "The Locked Diary & The Written Truth",
                "from_prompt": "A locked diary sits unopened.",
                "to_prompt": "The locked diary’s lock clicks, its pages turn, and words begin to write themselves."
            },
            {
                "title": "The Muffled Voice & The Clear Echo",
                "from_prompt": "A mouth remains closed, unable to speak.",
                "to_prompt": "The mouth’s lips part, and a voice emerges from it, clear, powerful, and true."
            }
        ]
    },
    "Disassociated": {
        "transformation_to": "Embodied",
        "prompts": [
            {
                "title": "The Jumbled Puzzle & The Completed Masterpiece",
                "from_prompt": "Puzzle pieces float in the air, disconnected.",
                "to_prompt": "The puzzle pieces snap into place, forming a breathtaking masterpiece."
            },
            {
                "title": "The Hollow Mannequin & The Breathing Body",
                "from_prompt": "A mannequin stands still in a storefront, lifeless.",
                "to_prompt": "The mannequin’s joints soften, color flushes into its skin, and it breathes deeply."
            }
        ]
    },
    "Ruminating": {
        "transformation_to": "Present",
        "prompts": [
            {
                "title": "The Stormy Sky & The Clear Horizon",
                "from_prompt": "Dark clouds swirl chaotically.",
                "to_prompt": "The wind calms, and the dark clouds part, revealing a vast blue sky and a radiant sun."
            },
            {
                "title": "The Endless Echo & The Silent Stillness",
                "from_prompt": "A canyon filled with echoing, overlapping voices.",
                "to_prompt": "The canyon’s echoing voices dissolve, replaced by a single deep breath, reflecting clarity."
            }
        ]
    },
    "Hypervigilant": {
        "transformation_to": "Relaxed",
        "prompts": [
            {
                "title": "The Overgrown Garden & The Flowing Zen Stream",
                "from_prompt": "A chaotic, tangled garden.",
                "to_prompt": "The chaotic, tangled garden reshapes into a peaceful Japanese zen garden with a tranquil stream."
            }
        ]
    },
    "Illness": {
        "transformation_to": "Health",
        "prompts": [
            {
                "title": "The Broken Wing & The Rising Flight",
                "from_prompt": "A bird struggles, one wing weak.",
                "to_prompt": "Feathers regrow on the bird, and it soars into the open sky."
            }
        ]
    },
    "Oppression": {
        "transformation_to": "Freedom",
        "prompts": [
            {
                "title": "The Caged Bird & The Open Sky",
                "from_prompt": "A bird flutters against a glass wall, trapped.",
                "to_prompt": "The glass wall shatters, and the bird soars into a vast open sky."
            }
        ]
    },
    "Scarcity": {
        "transformation_to": "Abundance",
        "prompts": [
            {
                "title": "The Barren Tree & The Orchard of Gold",
                "from_prompt": "A lone, lifeless tree stands in dry earth.",
                "to_prompt": "The lone, lifeless tree blossoms, and golden fruits cover its branches."
            }
        ]
    },
    "Controlling": {
        "transformation_to": "Flexible",
        "prompts": [
            {
                "title": "The Iron Cage & The Unfolding Petals",
                "from_prompt": "A metallic cage sits locked, rigid.",
                "to_prompt": "The metallic cage’s bars soften into vines, blooming into radiant flowers."
            }
        ]
    },
    "Codependent": {
        "transformation_to": "Authentic Autonomy",
        "prompts": [
            {
                "title": "The Entwined Vines & The Thriving Forest",
                "from_prompt": "two vines wrap around each other, tangled.",
                "to_prompt": "The two vines grow strong and independent, yet thrive side by side."
            }
        ]
    },
    "Feeling Excluded": {
        "transformation_to": "Belonging",
        "prompts": [
            {
                "title": "The Wandering Star & The Constellation",
                "from_prompt": "A single star drifts in a vast, empty sky.",
                "to_prompt": "Galaxies appear, forming a glowing constellation around the single star."
            }
        ]
    },
    "Safety & Comfort": {
        "transformation_to": "Embracing Transformation",
        "prompts": [
            {
                "title": "The Cocoon & The Butterfly",
                "from_prompt": "A cocoon remains tightly wrapped, safe but confined.",
                "to_prompt": "The cocoon cracks, and a butterfly emerges from it, embracing the open sky."
            }
        ]
    },
    "Shame": {
        "transformation_to": "Healthy Pride",
        "prompts": [
            {
                "title": "The Extinguished Candle & The Lantern's Glow",
                "from_prompt": "A melted candle sits in darkness.",
                "to_prompt": "A tiny spark rekindles the melted candle into a bright flame."
            }
        ]
    },
    "External Validation": {
        "transformation_to": "Wholeness",
        "prompts": [
            {
                "title": "The Mirror & The Inner Light",
                "from_prompt": "A person looks into a mirror, seeking reflection.",
                "to_prompt": "The mirror fades, and the person’s inner light glows brightly from within."
            }
        ]
    },
    "Controlling My Body": {
        "transformation_to": "Listening to My Body",
        "prompts": [
            {
                "title": "The Rigid Marionette & The Free Dancer",
                "from_prompt": "A puppet moves stiffly, controlled by strings.",
                "to_prompt": "The puppet’s strings dissolve, and it dances freely, moving with grace."
            }
        ]
    }
}

class CombinePromptsNode:
    """
    Combines emotion and transformation prompts into a structured, coherent prompt.
    Places the transformation and emotion components in appropriate context.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "transformation_from": ("STRING", {"default": "uncertainty"}),
                "transformation_to": ("STRING", {"default": "confidence"}),
                "emotion_scores": ("DICT", {"default": {}}),
                "transformation_prompts": ("DICT", {"default": {}}),
                "emotion_prompts": ("DICT", {"default": {}}),
                "base_style": ("STRING", {"default": "surreal, high quality, detailed"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("combined_prompt", "from_prompt", "to_prompt")
    FUNCTION = "combine_prompts"
    CATEGORY = "Sphinx"


    def fetch_fresh_emotion_data(self):
        """
        Fetches the latest emotion data from the API endpoint.
        Returns the updated emotion scores or None if the fetch fails.
        """
        try:
            emotions_url = "http://127.0.0.1:8010/get_emotion_data"
            response = requests.get(emotions_url)
            if response.status_code == 200:
                data = response.json()
                fresh_emotions = data.get("emotions", {})
                print("✅ CombinePromptsNode fetched fresh emotion data:", fresh_emotions, flush=True)
                return fresh_emotions
            else:
                print(f"⚠️ CombinePromptsNode: Error fetching emotions: {response.status_code}", flush=True)
                return None
        except Exception as e:
            print(f"⚠️ CombinePromptsNode: Exception fetching emotions: {str(e)}", flush=True)
            return None

    def combine_prompts(self, transformation_from, transformation_to, 
                       emotion_scores, transformation_prompts, emotion_prompts,
                       base_style=""):
        print(f"DEBUG: Combining prompts for {transformation_from} to {transformation_to}", flush=True)
        
        # Fetch fresh emotion data
        fresh_emotions = self.fetch_fresh_emotion_data()
        if fresh_emotions:
            emotion_scores = fresh_emotions
            print("✅ CombinePromptsNode updated emotion scores:", emotion_scores, flush=True)
        else:
            print("⚠️ CombinePromptsNode: Failed to fetch fresh emotion data", flush=True)
            
        
        # Get transformation prompt if available
        # Try different formats of keys to find a match
        trans_key = f"{transformation_from.lower()}_to_{transformation_to.lower()}".replace(" ", "_")
        trans_prompt = None
        
        # Try to find the transformation prompt
        if trans_key in transformation_prompts:
            trans_prompt = transformation_prompts[trans_key]
        else:
            # Try alternative formats
            for key in transformation_prompts:
                if transformation_from.lower() in key.lower() and transformation_to.lower() in key.lower():
                    trans_prompt = transformation_prompts[key]
                    break
        
        if not trans_prompt:
            # Use the transformation names directly if no prompt found
            trans_prompt = f"transformation from {transformation_from} to {transformation_to}"
            
        # Sort emotions by score and get top emotions
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        top_emotions = [e[0] for e in sorted_emotions if e[1] >= 0.1][:3]  # Use top 3 significant emotions

        # Format the emotion part of the prompt with proper weighting
        emotion_prompt_parts = []
        emotion_descriptions = []

        try:
            # Get emotion prompts for top emotions
            for emotion in top_emotions:
                # Get the score for weighting
                score = next((s[1] for s in sorted_emotions if s[0] == emotion), 0.0)
                
                # Format with proper weighting syntax
                if emotion in emotion_prompts and emotion_prompts[emotion].strip():
                    # For visual prompts, use the emotion_prompts dictionary
                    prompt_text = emotion_prompts[emotion].strip()
                    # Add weighted prompt for visual elements
                    weight = min(round(score * 10, 1), 1.3)  # Cap at 1.3
                    if weight >= 0.03:  # Only include if weight is significant
                        emotion_prompt_parts.append(f"{prompt_text}:{weight}")
                
                # Also collect the emotion names themselves for the description
                emotion_descriptions.append(emotion)
        except Exception as e:
            print(f"DEBUG: Error processing emotion prompts for {top_emotions}: {str(e)}", flush=True)

        # Get transformation prompts if available
        from_visual_prompt = ""
        to_visual_prompt = ""

        # Look for matching transformation in our dictionary
        if transformation_from in TRANSFORMATION_PROMPTS:
            trans_data = TRANSFORMATION_PROMPTS[transformation_from]
            if trans_data["prompts"] and len(trans_data["prompts"]) > 0:
                # Use the first prompt in the list
                prompt_data = trans_data["prompts"][0]
                from_visual_prompt = prompt_data.get("from_prompt", "")
                to_visual_prompt = prompt_data.get("to_prompt", "")

        # Create coherent prompt structure with improved weighting and formatting
        # Main prompt for the scene with transformation focus
        combined_prompt = f"The main subject shows transformation from {transformation_from} to {transformation_to}"
        
        # Add visual prompts to combined prompt if available
        if from_visual_prompt and to_visual_prompt:
            combined_prompt = f"The main subject shows transformation from {transformation_from} to {transformation_to}: {from_visual_prompt} transforming to {to_visual_prompt}"

        # Add emotional atmosphere
        if emotion_descriptions:
            emotion_text = ", ".join(emotion_descriptions[:2])  # Limit to top 2 for clarity
            combined_prompt += f", expressing moving from {emotion_text} to more positive emotions."

        # Add visual elements from emotion prompts with their weights
        if emotion_prompt_parts:
            combined_prompt += f", {', '.join(emotion_prompt_parts)}"

        # Create specific from/to prompts with emotional context
        # From prompt with transformation details
        from_prompt = f"The subject appears {transformation_from}, expressing {emotion_text}"
        if from_visual_prompt:
            from_prompt = from_visual_prompt

        # To prompt with transformation details
        to_prompt = f"The subject transforms to {transformation_to}"
        if to_visual_prompt:
            to_prompt = to_visual_prompt
        
        # Add style if provided
        if base_style:
            combined_prompt += f", {base_style}"
            from_prompt += f", {base_style}"
            to_prompt += f", {base_style}"

        
        print(f"DEBUG: Final combined prompt: {combined_prompt}", flush=True)
        print(f"DEBUG: From prompt: {from_prompt}", flush=True)
        print(f"DEBUG: To prompt: {to_prompt}", flush=True)
        
        return (combined_prompt, from_prompt, to_prompt)

NODE_CLASS_MAPPINGS = {
    "CombinePromptsNode": CombinePromptsNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CombinePromptsNode": "Combine Emotion & Transformation Prompts into overall prompt"
}
