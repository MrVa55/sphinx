# CombinePromptsNode.py

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

    def combine_prompts(self, transformation_from, transformation_to, 
                       emotion_scores, transformation_prompts, emotion_prompts,
                       base_style=""):
        print(f"DEBUG: Combining prompts for {transformation_from} to {transformation_to}", flush=True)
        
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
        top_emotions = [e[0] for e in sorted_emotions if e[1] >= 0.1][:2]  # Use top 2 significant emotions
        
        emotion_prompt_parts = []
        try:
            # Get emotion prompts for top emotions
            for emotion in top_emotions:
                if emotion in emotion_prompts and emotion_prompts[emotion].strip():
                    emotion_prompt_parts.append(emotion_prompts[emotion].strip())
        except:
            print(f"DEBUG: Error getting emotion prompts for {top_emotions}", flush=True)
        
        # Create coherent prompt structure
        # Main prompt is the transformation with emotional context and style
        combined_prompt = f"The main subject shows {trans_prompt}"

                
        # Create from prompt with emotional context
        from_prompt = f"The main subject shows {transformation_from}"
        
        # Create to prompt with emotional context
        to_prompt = f"The main subject shows {transformation_to}"
        
        # Add emotional context as background/mood
        if emotion_prompt_parts:
            emotion_text = " and ".join(emotion_prompt_parts)
            combined_prompt += f", with background and mood reflecting {emotion_text}"
            from_prompt += f", with background and mood reflecting {emotion_text}"
            to_prompt += f", with background and mood reflecting {emotion_text}"
        
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
