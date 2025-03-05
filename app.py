import whisper
import tempfile
import os
from fastapi import FastAPI, File, UploadFile
from transformers import pipeline
from diffusers import StableDiffusionPipeline
import torch
import uvicorn
app = FastAPI()

# Fix: Set cache dir to prevent redownloading models
os.environ["TRANSFORMERS_CACHE"] = "/root/.cache/huggingface"
os.environ["HF_HOME"] = "/root/.cache/huggingface"

# Load models
whisper_model = whisper.load_model("base")
emotion_classifier = pipeline(
    "text-classification", 
    model="joeddav/distilbert-base-uncased-go-emotions-student", 
    top_k=None,
    device=0  # Explicitly set to GPU
)

sd_pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5").to("cuda")  # Load SD model

def generate_prompt(emotions):
    """
    Converts emotion scores into a Stable Diffusion prompt.
    """
    emotion_descriptions = {
        "joy": "a vibrant, colorful, sunny landscape full of life and happiness",
        "sadness": "a dark, rainy, moody environment filled with sorrow",
        "anger": "a fiery, chaotic scene with red tones and intense energy",
        "fear": "a dark forest with eerie shadows and a sense of mystery",
        "surprise": "a surreal dreamlike world with unexpected shapes and colors",
        "love": "a warm, romantic sunset with soft glowing light"
    }

    # Sort emotions by confidence and create a blended prompt
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    prompt = ", ".join([f"{emotion_descriptions[e[0]]} ({e[1]:.2f})" for e in sorted_emotions if e[0] in emotion_descriptions])

    return prompt if prompt else "a neutral scene with balanced colors"

@app.post("/transcribe_and_generate")
async def transcribe_and_generate(file: UploadFile = File(...)):
    """
    Transcribes an audio file, detects emotions, and generates an image based on detected emotions.
    """
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp_filename = tmp.name
        content = await file.read()
        tmp.write(content)

    # Run Whisper for transcription
    result = whisper_model.transcribe(tmp_filename)
    text = result["text"]

    # Delete temp file
    os.remove(tmp_filename)

    # Run emotion classification (returns all emotion scores)
    emotions = emotion_classifier(text)
    emotion_results = {e["label"]: e["score"] for e in emotions[0]}  # Extract label-score pairs

    # Generate Stable Diffusion prompt
    prompt = generate_prompt(emotion_results)

    # Generate image using Stable Diffusion
    image = sd_pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]

    # Save image temporarily
    output_filename = "output.png"
    image.save(output_filename)

    return {"transcription": text, "emotions": emotion_results, "prompt": prompt, "image": output_filename}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)