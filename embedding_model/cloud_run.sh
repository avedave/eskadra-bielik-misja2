#!/bin/bash

gcloud run deploy $EMBEDDING_SERVICE \
  --source . \
  --region $REGION \
  --concurrency 4 \
  --cpu 8 \
  --no-allow-unauthenticated \
  --set-env-vars OLLAMA_NUM_PARALLEL=4 \
  --max-instances 1 \
  --memory 16Gi \
  --timeout=600 \
  --labels dev-tutorial=dos-codelab-bielik-rag