FROM runpod/stable-diffusion-webui:7.4.4

# Install whisper + fastapi + uvicorn
RUN pip install fastapi uvicorn git+https://github.com/openai/whisper.git

# Copy over your app code, etc.
COPY app.py /workspace/app.py

# Expose your port
EXPOSE 8010

CMD ["python", "/workspace/app.py"]

