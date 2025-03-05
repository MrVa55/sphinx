# Use a RunPod Stable Diffusion WebUI base image
FROM runpod/stable-diffusion-webui:7.4.4

# Set environment variable to fix TensorFlow conflicts
ENV TF_ENABLE_ONEDNN_OPTS=0
ENV CUDA_VISIBLE_DEVICES=0

# Install required dependencies
RUN python3 -m pip install --upgrade pip \
    && pip install websockets xformers fastapi python-multipart uvicorn \
    torch torchvision diffusers pillow transformers accelerate \
    git+https://github.com/openai/whisper.git

# Set the working directory
WORKDIR /app

# Copy application code into container
COPY app.py /app/app.py


# Append FastAPI startup command to the original `/start.sh`
RUN echo 'nohup python3 /app/app.py &> /workspace/logs/fastapi.log &' >> /start.sh

# Expose port 8010 for the FastAPI server
EXPOSE 8010

# Expose ports for Jupyter (8888), WebUI (7860)
EXPOSE 7860 8888

# Run a startup test to check CUDA & PyTorch versions (logs will show during build)
RUN python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda)"
RUN nvcc --version

# Pre-download Whisper model
RUN python -c "import whisper; whisper.load_model('base')"

# Pre-download Emotion Analysis Model
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='joeddav/distilbert-base-uncased-go-emotions-student')"

# Pre-download Stable Diffusion model
RUN python -c "from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('runwayml/stable-diffusion-v1-5')"

# Ensure the original entrypoint & CMD are inherited
ENTRYPOINT ["/opt/nvidia/nvidia_entrypoint.sh"]
CMD ["/start.sh"]
