class StaticTextNode:
    """
    A simple node that displays the emotion data received from EmotionDisplayNode.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "emotions": ("STRING", {"default": "test", "forceInput": True})  # Added forceInput
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Processed Text",)
    FUNCTION = "display_text"
    CATEGORY = "Debug"
    OUTPUT_NODE = True

    def display_text(self, emotions):
        print("==== StaticTextNode Debug ====", flush=True)
        print(f"Type of received input: {type(emotions)}", flush=True)
        print(f"Content of received input: {emotions}", flush=True)
        print("============================", flush=True)
        return (emotions,)

NODE_CLASS_MAPPINGS = {
    "Static Text": StaticTextNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Static Text": "Static Text Node"
}
