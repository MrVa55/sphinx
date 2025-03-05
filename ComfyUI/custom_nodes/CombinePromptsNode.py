# CombineEmotionPromptsNode.py

class CombineEmotionPromptsNode:
    """
    This node combines a base prompt with emotion prompt fragments based on detected emotion scores.
    
    Inputs:
      - base_prompt: The main prompt provided by the user.
      - emotion_scores: A dictionary with emotion names as keys and their detected scores.
      - emotion_prompts: A dictionary mapping emotion names to user-defined prompt fragments.
      
    It selects the top two emotions (with non-empty prompt fragments) and appends their fragments to the base prompt.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"default": ""}),
                "emotion_scores": ("DICT", {"default": {}}),
                "emotion_prompts": ("DICT", {"default": {}})
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "combine_prompts"
    CATEGORY = "Custom/Emotions"

    def combine_prompts(self, base_prompt, emotion_scores, emotion_prompts):
        print("DEBUG: CombineEmotionPromptsNode input base_prompt:", base_prompt, flush=True)
        print("DEBUG: CombineEmotionPromptsNode input emotion_scores:", emotion_scores, flush=True)
        print("DEBUG: CombineEmotionPromptsNode input emotion_prompts:", emotion_prompts, flush=True)

        # Sort the detected emotions by score (highest first)
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        print("DEBUG: Sorted emotions:", sorted_emotions, flush=True)

        top_fragments = []
        for emotion, score in sorted_emotions:
            fragment = emotion_prompts.get(emotion, "").strip()
            if fragment:
                top_fragments.append(fragment)
            if len(top_fragments) >= 2:
                break

        print("DEBUG: Top fragments selected:", top_fragments, flush=True)
        final_prompt = base_prompt.strip()
        if top_fragments:
            final_prompt += " " + " ".join(top_fragments)
        print("DEBUG: CombineEmotionPromptsNode final prompt:", final_prompt, flush=True)
        # Return as a one-element tuple.
        return (final_prompt,)

NODE_CLASS_MAPPINGS = {
    "CombineEmotionPromptsNode": CombineEmotionPromptsNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CombineEmotionPromptsNode": "Combine Emotion Prompts Node"
}
