FROM runpod/stable-diffusion-webui:7.4.4

# Install whisper + fastapi + uvicorn
RUN python3 -m pip install --upgrade pip
RUN pip install fastapi python-multipart uvicorn torch transformers git+https://github.com/openai/whisper.git

# Copy over your app code, etc.
#COPY app.py /workspace/app.py

# Expose your port
EXPOSE 8010

# CMD ["/bin/bash", "-c", "sleep infinity"]

COPY app.py /app/app.py
WORKDIR /app
CMD ["python", "app.py"]

# Set the working directory to /workspace before running the app
#WORKDIR /workspace

# Start the app
#CMD ["/bin/bash", "-c", "sleep 5 && python /workspace/app.py"]

