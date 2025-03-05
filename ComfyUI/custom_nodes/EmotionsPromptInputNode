# EmotionsPromptsInputNode.py

class EmotionsPromptsInputNode:
    """
    This node provides text inputs for 27 emotions.
    Users can supply custom prompt fragments for each emotion.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "admiration": ("STRING", {"default": ""}),
                "amusement": ("STRING", {"default": ""}),
                "anger": ("STRING", {"default": ""}),
                "annoyance": ("STRING", {"default": ""}),
                "approval": ("STRING", {"default": ""}),
                "caring": ("STRING", {"default": ""}),
                "confusion": ("STRING", {"default": ""}),
                "curiosity": ("STRING", {"default": ""}),
                "desire": ("STRING", {"default": ""}),
                "disappointment": ("STRING", {"default": ""}),
                "disapproval": ("STRING", {"default": ""}),
                "disgust": ("STRING", {"default": ""}),
                "embarrassment": ("STRING", {"default": ""}),
                "excitement": ("STRING", {"default": ""}),
                "fear": ("STRING", {"default": ""}),
                "gratitude": ("STRING", {"default": ""}),
                "grief": ("STRING", {"default": ""}),
                "joy": ("STRING", {"default": ""}),
                "love": ("STRING", {"default": ""}),
                "nervousness": ("STRING", {"default": ""}),
                "optimism": ("STRING", {"default": ""}),
                "pride": ("STRING", {"default": ""}),
                "realization": ("STRING", {"default": ""}),
                "relief": ("STRING", {"default": ""}),
                "remorse": ("STRING", {"default": ""}),
                "sadness": ("STRING", {"default": ""}),
                "surprise": ("STRING", {"default": ""})
            }
        }

    RETURN_TYPES = ("DICT",)
    FUNCTION = "get_emotion_prompts"
    OUTPUT_NODE = True
    CATEGORY = "Custom/Emotions"

    def get_emotion_prompts(
        self,
        admiration,
        amusement,
        anger,
        annoyance,
        approval,
        caring,
        confusion,
        curiosity,
        desire,
        disappointment,
        disapproval,
        disgust,
        embarrassment,
        excitement,
        fear,
        gratitude,
        grief,
        joy,
        love,
        nervousness,
        optimism,
        pride,
        realization,
        relief,
        remorse,
        sadness,
        surprise,
    ):
        prompts = {
            "admiration": admiration,
            "amusement": amusement,
            "anger": anger,
            "annoyance": annoyance,
            "approval": approval,
            "caring": caring,
            "confusion": confusion,
            "curiosity": curiosity,
            "desire": desire,
            "disappointment": disappointment,
            "disapproval": disapproval,
            "disgust": disgust,
            "embarrassment": embarrassment,
            "excitement": excitement,
            "fear": fear,
            "gratitude": gratitude,
            "grief": grief,
            "joy": joy,
            "love": love,
            "nervousness": nervousness,
            "optimism": optimism,
            "pride": pride,
            "realization": realization,
            "relief": relief,
            "remorse": remorse,
            "sadness": sadness,
            "surprise": surprise,
        }
        print("DEBUG: EmotionsPromptsInputNode returning prompts:", prompts, flush=True)
        # Always return as a one-element tuple.
        return (prompts,)


NODE_CLASS_MAPPINGS = {
    "EmotionsPromptsInputNode": EmotionsPromptsInputNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EmotionsPromptsInputNode": "Emotion Prompts Input Node"
}
