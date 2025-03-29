class TransformationsPromptInputNode:
    """
    This node provides text inputs for transformation states.
    Users can supply custom prompt fragments for each transformation.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "closed_off_to_open": ("STRING", {"default": "A transition from being closed off to being open"}),
                "stagnant_to_creative": ("STRING", {"default": "A transition from stagnation to creativity"}),
                "fearful_to_trusting": ("STRING", {"default": "A transition from fear to trust"}),
                "hiding_to_visible": ("STRING", {"default": "A transition from hiding to visibility"}),
                "uncentered_to_centered": ("STRING", {"default": "A transition from being uncentered to centered"}),
                "silenced_to_honest": ("STRING", {"default": "A transition from silence to honesty"}),
                "disassociated_to_embodied": ("STRING", {"default": "A transition from disassociation to embodiment"}),
                "ruminating_to_present": ("STRING", {"default": "A transition from rumination to presence"}),
                "hypervigilant_to_relaxed": ("STRING", {"default": "A transition from hypervigilance to relaxation"}),
                "illness_to_health": ("STRING", {"default": "A transition from illness to health"}),
                "oppression_to_freedom": ("STRING", {"default": "A transition from oppression to freedom"}),
                "scarcity_to_abundance": ("STRING", {"default": "A transition from scarcity to abundance"}),
                "controlling_to_flexible": ("STRING", {"default": "A transition from being controlling to flexible"}),
                "codependent_to_autonomous": ("STRING", {"default": "A transition from codependence to authentic autonomy"}),
                "excluded_to_belonging": ("STRING", {"default": "A transition from feeling excluded to belonging"}),
                "safety_to_transformation": ("STRING", {"default": "A transition from safety/comfort to embracing transformation"}),
                "shame_to_pride": ("STRING", {"default": "A transition from shame to healthy pride"}),
                "external_to_wholeness": ("STRING", {"default": "A transition from external validation to wholeness"}),
                "controlling_body_to_listening": ("STRING", {"default": "A transition from controlling my body to listening to my body"}),
            }
        }

    RETURN_TYPES = ("DICT",)
    FUNCTION = "get_transformation_prompts"
    OUTPUT_NODE = True
    CATEGORY = "Custom/Transformations"

    def get_transformation_prompts(self, **kwargs):
        # Return all the inputs as a dictionary
        print("DEBUG: TransformationsPromptInputNode returning prompts:", kwargs, flush=True)
        return (kwargs,)


NODE_CLASS_MAPPINGS = {
    "TransformationsPromptInputNode": TransformationsPromptInputNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TransformationsPromptInputNode": "Transformation Prompts Input Node"
} 