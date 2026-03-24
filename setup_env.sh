#!/bin/bash

# Ustawienie zmiennych środowiskowych
export PROJECT_ID=$(gcloud config get-value project)
export REGION="europe-west1"
export EMBEDDING_SERVICE="embedding-gemma"
export LLM_SERVICE="bielik"
export BIGQUERY_DATASET="rag_dataset"
export BIGQUERY_TABLE="hotel_rules"

echo "Wczytano zmienne środowiskowe"