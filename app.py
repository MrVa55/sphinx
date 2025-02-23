import whisper
import tempfile
import os
from fastapi import FastAPI, File, UploadFile
from transformers import pipeline
import uvicorn

app = FastAPI()

# Load models
# Load model safely
whisper_model = whisper.load_model("base")
emotion_classifier = pipeline(
    "text-classification",
    model="joeddav/distilbert-base-uncased-go-emotions-student",
    top_k=None  # Use this instead of return_all_scores=True
)

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribes an audio file and detects multiple emotions with confidence scores.
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

    # Convert the output to a structured response
    emotion_results = {e["label"]: e["score"] for e in emotions[0]}  # Extract label-score pairs

    return {
        "transcription": text,
        "emotions": emotion_results  # Dict of all detected emotions and confidence scores
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
