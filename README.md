# Sphinx - Emotional Response Visualization

Sphinx is a therapeutic visualization system developed for the Luma AI hackathon. It combines voice transcription, sentiment analysis, and AI-generated videos to create a unique therapeutic experience based on a user's emotional responses.

## Overview

Sphinx creates a therapeutic experience by:

1. Capturing the user's voice through a microphone
2. Transcribing speech using OpenAI's Whisper model
3. Analyzing the emotional content of the transcription
4. Generating a prompt based on the detected emotions
5. Using the Luma Labs API to create a video based on the prompt
6. Displaying the video in an immersive experience

The system is designed to help users reflect on their thoughts and feelings through a guided conversational experience, with real-time visual feedback that represents their emotional state.

## Architecture

The project consists of several key components:

### Backend (FastAPI)

- **app.py**: Main application server that handles API requests, audio transcription, and emotion analysis
- **workflow_manager.py**: Manages the ComfyUI workflow for generating images based on emotions

### Frontend

- **index.html**: Dashboard interface for recording speech and viewing results
- **projection.html**: Immersive experience interface for guided therapeutic sessions
- **script.js**: Conversation script for the guided experience

### ComfyUI Custom Nodes

- **EmotionImportNode.py**: Imports emotion data from the API
- **EmotionsPromptInputNode.py**: Provides text inputs for different emotions
- **CombinePromptsNode.py**: Combines base prompts with emotion-specific prompts
- **CustomStreamNode.py**: Handles image streaming
- **sphinx_stream.py**: WebSocket implementation for streaming images
- **global_vars.py**: Manages global variables across nodes

## Features

- **Voice Recording**: Capture user speech through the browser's microphone
- **Speech Transcription**: Convert speech to text using OpenAI's Whisper model
- **Emotion Analysis**: Analyze text for emotional content using a pre-trained model
- **Dynamic Visualization**: Generate videos through Luma Labs API that reflect the detected emotions
- **Guided Experience**: Follow a therapeutic conversation flow with visual feedback
- **Real-time Updates**: See visualizations update as emotions are detected

## Technical Details

### Models Used

- **Speech Recognition**: OpenAI Whisper (base model)
- **Emotion Classification**: DistilBERT-based emotion classifier (joeddav/distilbert-base-uncased-go-emotions-student)
- **Video Generation**: Luma Labs API

### Emotion Processing Pipeline

1. Audio is captured and sent to the server
2. Whisper transcribes the audio to text
3. The emotion classifier analyzes the text and assigns scores to 27 different emotions
4. The top emotions are selected and combined with visual prompt fragments
5. The combined prompt is sent to the Luma Labs API to generate a video
6. The video is streamed back to the client for display

### Deployment

The application is containerized using Docker and can be deployed on platforms that support GPU acceleration, such as RunPod. The Dockerfile sets up all necessary dependencies and configures the environment for running both the FastAPI server and ComfyUI.

## Getting Started

### Prerequisites

- CUDA-capable GPU
- Docker
- Python 3.8+

### Running Locally

1. Clone the repository
2. Build the Docker image: `docker build -t sphinx .`
3. Run the container: `docker run --gpus all -p 8010:8010 -p 3020:3020 sphinx`
4. Access the dashboard at `http://localhost:8010`
5. Access the immersive experience at `http://localhost:8010/projection`

### Using the Application

1. On the dashboard, click "Start Recording" to begin capturing your voice
2. Speak into your microphone
3. Click "Stop Recording" when finished
4. The system will display your transcribed speech, detected emotions, and a generated video
5. For the guided experience, navigate to the projection page and follow the prompts

## The Therapeutic Experience

The guided experience asks reflective questions such as:

1. "What is the thought that most inhibits you from achieving what you want in your life?"
2. "If this limiting thought were suddenly removed, what would you do differently?"

As you respond, the system analyzes your emotional state and generates videos that reflect your feelings, creating a unique and personalized therapeutic journey.

## License

See the LICENSE file for details.
