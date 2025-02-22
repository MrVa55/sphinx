import uvicorn
from fastapi import FastAPI, File, UploadFile
import whisper
import tempfile
import os

app = FastAPI()

# Load Whisper model at startup
# "base", "small", "medium", "large" etc. Pick depending on GPU power & speed needs
model = whisper.load_model("base")  

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp_filename = tmp.name
        content = await file.read()
        tmp.write(content)

    # Use whisper to transcribe
    result = model.transcribe(tmp_filename)
    text = result["text"]

    # Cleanup temp file
    os.remove(tmp_filename)
    
    return {"transcription": text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
