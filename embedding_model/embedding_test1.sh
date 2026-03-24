#!/bin/bash

#uzyskanie URL usługi LLM
export EMBEDDING_SERVICE_URL=$(gcloud run services describe $EMBEDDING_SERVICE --region $REGION --format="value(status.url)")

#uzyskanie tokenu autoryzacyjnego
export ID_TOKEN=$(gcloud auth print-identity-token)

curl -X POST "$EMBEDDING_SERVICE_URL/api/embed" \
    -H "Authorization: Bearer $ID_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "embeddinggemma",
        "input": "Sample text"
    }'