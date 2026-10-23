import os
import csv
import io
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.auth.transport.requests
import google.oauth2.id_token
from google.cloud import bigquery

app = FastAPI(title="RAG API (Bielik & EmbeddingGemma)")

# Zapewnij, że katalog static istnieje
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

PROJECT_ID = os.environ.get("PROJECT_ID")
DATASET_ID = os.environ.get("BIGQUERY_DATASET", "rag_dataset")
TABLE_ID = os.environ.get("BIGQUERY_TABLE", "hotel_rules")
REGION = os.environ.get("REGION", "europe-west1")
EMBEDDING_URL = os.environ.get("EMBEDDING_URL")
LLM_URL = os.environ.get("LLM_URL")

bq_client = bigquery.Client(project=PROJECT_ID) if PROJECT_ID else None

def get_id_token(audience: str) -> str:
    """Fetch an identity token for the given external Cloud Run URL."""
    try:
        # Pobrane dla lokalnego testowania, jako fallback jeśli jesteśmy w Cloud Run
        request = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(request, audience)
        return token
    except Exception as e:
        print(f"Błąd podczas pobierania tokenu za pomocą google.oauth2.id_token dla {audience}: {e}")
        # Próba bezpośredniego pobrania ze spersonalizowanego gcloud auth print-identity-token w środowisku dev
        token = os.popen("gcloud auth print-identity-token").read().strip()
        return token

def get_embedding(text: str) -> list[float]:
    if not EMBEDDING_URL:
        raise ValueError("EMBEDDING_URL variable is not set")
    
    url = f"{EMBEDDING_URL}/api/embed"
    token = get_id_token(EMBEDDING_URL)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "embeddinggemma-2:270m",
        "input": text
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    # Zakładamy odpowiedź z modelem `embed` z Ollama
    return response.json().get("embeddings", [[]])[0]

class AskRequest(BaseModel):
    query: str

@app.post("/ingest")
async def ingest_csv(file: UploadFile = File(...)):
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized (missing PROJECT_ID)")
    
    content = await file.read()
    csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    
    rows_to_insert = []
    
    for row in csv_reader:
        doc_id = row.get("id")
        text = row.get("text")
        
        if not doc_id or not text:
            continue
            
        try:
            embedding = get_embedding(text)
            rows_to_insert.append({
                "id": doc_id,
                "content": text,
                "embedding": embedding
            })
        except Exception as e:
            print(f"Błąd w generowaniu osadzenia dla '{text}': {e}")
            
    if rows_to_insert:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        errors = bq_client.insert_rows_json(table_ref, rows_to_insert)
        if errors:
            raise HTTPException(status_code=500, detail=f"Błąd wstawiania do BigQuery: {errors}")
            
    return {"status": "success", "inserted_count": len(rows_to_insert)}

@app.post("/ask")
async def ask_question(request_data: AskRequest):
    if not bq_client:
        raise HTTPException(status_code=500, detail="BigQuery client not initialized (missing PROJECT_ID)")
        
    query = request_data.query
    
    try:
        query_embedding = get_embedding(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania wektora zapytania: {e}")
        
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    # Krok 1: Wyszukiwanie Wektorowe w BigQuery
    bq_query = f"""
    SELECT base.content, distance
    FROM VECTOR_SEARCH(
      TABLE `{table_ref}`,
      'embedding',
      (SELECT {query_embedding} as embedding),
      top_k => 3,
      distance_type => 'COSINE'
    )
    """
    try:
        query_job = bq_client.query(bq_query)
        results = query_job.result()
        context_docs = [row.content for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd przeszukiwania wektorowego w BigQuery: {e}")
        
    # Krok 2: Przygotowanie Kontekstu i Wiadomości do LLM
    context_text = "\\n\\n".join(context_docs)
    
    prompt = (
        f"Jesteś pomocnym asystentem odpowiadającym na pytania dotyczące zasad hotelowych. "
        f"Odpowiedz na poniższe pytanie bazując TYLKO na dostarczonym kontekście.\\n\\n"
        f"KONTEKST:\\n{context_text}\\n\\n"
        f"PYTANIE:\\n{query}"
    )
    
    if not LLM_URL:
        raise HTTPException(status_code=500, detail="LLM_URL variable is not set")
        
    token = get_id_token(LLM_URL)
    url = f"{LLM_URL}/api/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "SpeakLeash/bielik-4.5b-v3.0-instruct:Q8_0",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas komunikacji z modelem LLM: {e}")
        
    return {
        "answer": answer,
        "context_used": context_docs
    }

@app.post("/ask_direct")
async def ask_direct(request_data: AskRequest):
    query = request_data.query

    if not LLM_URL:
        raise HTTPException(status_code=500, detail="LLM_URL variable is not set")
        
    token = get_id_token(LLM_URL)
    url = f"{LLM_URL}/api/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Odpowiedz na poniższe pytanie w sposób jasny i zwięzły:\\n\\nPYTANIE:\\n{query}"
    
    payload = {
        "model": "SpeakLeash/bielik-4.5b-v3.0-instruct:Q8_0",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas komunikacji z modelem LLM: {e}")
        
    return {
        "answer": answer
    }
