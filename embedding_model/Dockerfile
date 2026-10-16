#FROM ollama/ollama:latest
#embeddinggemma-2 requires Ollama 0.40.4 or newer. This service runs on CPU only,
#so the NVIDIA L4 compatibility issue that pins llm/Dockerfile to 0.23.4 does not apply here.
FROM ollama/ollama:0.40.5

# Listen on all interfaces, port 8080
ENV OLLAMA_HOST=0.0.0.0:8080

# Store model weight files in /models
ENV OLLAMA_MODELS=/models

# Reduce logging verbosity
ENV OLLAMA_DEBUG=false

# Never unload model weights from the GPU
ENV OLLAMA_KEEP_ALIVE=-1

# Store the model weights in the container image
ENV MODEL=embeddinggemma-2:270m
RUN ollama serve & sleep 5 && ollama pull $MODEL

# Start Ollama
ENTRYPOINT ["ollama", "serve"]