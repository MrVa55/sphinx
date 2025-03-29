# Use a RunPod Stable Diffusion WebUI base image
FROM runpod/stable-diffusion-webui:7.4.4

# Set environment variables to fix TensorFlow conflicts and select the CUDA device
ENV TF_ENABLE_ONEDNN_OPTS=0
ENV CUDA_VISIBLE_DEVICES=0

# Upgrade pip and install required Python packages.
RUN python3 -m pip install --upgrade pip && \
    pip install websockets xformers fastapi python-multipart uvicorn \
    torch torchvision diffusers pillow transformers accelerate \
    git+https://github.com/openai/whisper.git

# Set the working directory
WORKDIR /workspace/app

# Create directories for our app files
RUN mkdir -p /sphinxfiles/app
RUN mkdir -p /sphinxfiles/ComfyUI/custom_nodes

# Copy the entire app directory to sphinxfiles
COPY ./app/ /sphinxfiles/app/

# Copy ComfyUI custom nodes
COPY ./ComfyUI/custom_nodes/ /sphinxfiles/ComfyUI/custom_nodes/

# Append FastAPI startup command to the original `/start.sh`
RUN echo 'nohup python3 /app/app.py &> /workspace/logs/fastapi.log &' >> /start.sh

# Remove the original sleep infinity from start.sh
RUN sed -i '/sleep infinity/d' /start.sh

# Copy the new start.sh into the container
COPY start.sh /start.sh
# And ensure it is executable
RUN chmod +x /start.sh

# Expose necessary ports: FastAPI (8010), WebUI (7860), Jupyter (8888)
EXPOSE 8010 7860 8888

# Run tests to check CUDA & PyTorch versions (logs will show during build)
RUN python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda)" && \
    nvcc --version

# Pre-download models to speed up runtime requests.
RUN python -c "import whisper; whisper.load_model('base')"
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='joeddav/distilbert-base-uncased-go-emotions-student')"
RUN python -c "from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('runwayml/stable-diffusion-v1-5')"

# Inherit the original entrypoint & CMD
ENTRYPOINT ["/opt/nvidia/nvidia_entrypoint.sh"]
CMD ["/start.sh"]
