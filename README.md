# Eskadra Bielik - Misja 2 - RAG w oparciu o model Bielik i Google Cloud

Suwerenne i wiarygodne AI - Od dokumentów firmowych do inteligentnej bazy wiedzy w oparciu o model Bielik i Google Cloud.

## O projekcie

Niniejsze repozytorium prezentuje kompletne, bezserwerowe (serverless) rozwiązanie klasy RAG (Retrieval-Augmented Generation) wdrożone w chmurze Google Cloud. Głównym celem aplikacji jest dostarczenie wydajnego i suwerennego inteligentnego asystenta zdolnego do odpowiadania na pytania użytkownika w oparciu o dedykowaną bazę wiedzy (np. wewnętrzne dokumenty, regulaminy).

Podstawowa architektura wdrażanego rozwiązania opiera się na poniższych serwisach i komponentach:
- **Modelu językowym LLM:** Suwerenny polski model [Bielik](https://ollama.com/SpeakLeash/bielik-4.5b-v3.0-instruct) charakteryzujący się bardzo dobrym zrozumieniem języka polskiego oraz polskiego kontekstu kulturowego. Uruchomiony w usłudze Cloud Run, odpowiada za ostateczne generowanie naturalnej dla użytkownika odpowiedzi.
- **Modelu osadzania (Embedding):** Wydajny model [EmbeddingGemma](https://deepmind.google/models/gemma/embeddinggemma/) uruchomiony w usłudze Cloud Run, służący do szybkiej zamiany tekstu (zapytań użytkownika i dokumentów docelowych) na reprezentację wektorową.
- **Wektorowej Bazie Wiedzy:** Skalowalna hurtownia danych [BigQuery](https://cloud.google.com/bigquery?hl=en) z mechanizmem Vector Search zapewniająca wektorowe wyszukiwanie semantycznie dopasowanych fragmentów z pośród milionów dokumentów źródłowych.
- **Logice i serwerze aplikacyjnym:** Aplikacja napisana w języku Python (z frameworkiem FastAPI), udostępniająca nakładkę graficzną Web UI oraz publiczne API spinające platformy w całość.

Dodatkowo, dzięki prostemu interfejsowi graficznemu, aplikacja pozwala na wygodne porównanie i empiryczne przetestowanie "surowego" modelu Bielik polegającego tylko na sobie w konfrontacji z bogatszym strumieniem odpowiedzi nowocześniejszego RAG wspomaganego dedykowanym własnym kontekstem.


## Z czego składa się kod?

Przykładowy kod źródłowy zawarty w tym repozytorium pozwala w szczególności na:

* Skonfigurowanie własnej instancji modelu [Bielik](https://ollama.com/SpeakLeash/bielik-4.5b-v3.0-instruct) w oparciu o silnik [Ollama](https://ollama.com/)

* Skonfigurowanie własnej instancji modelu osadzającego (embedding model) [EmbeddingGemma](https://deepmind.google/models/gemma/embeddinggemma/) w oparciu o [Ollama](https://ollama.com/)

* Uruchomienie obu powyższych modeli na platformie typu bezserwerowego: [Cloud Run](https://cloud.google.com/run?hl=en)

* Skonfigurowanie bazy wektorów w [BigQuery](https://cloud.google.com/bigquery?hl=en) wraz ze specjalnym zaawansowanym przeszukiwaniem [BigQuery Vector Search](https://docs.cloud.google.com/bigquery/docs/vector-search)

## 1. Przygotowanie projektu Google Cloud

1. Uzyskaj kredyt Cloud **OnRamp**, lub skonfiguruj płatności w projekcie Google Cloud

2. Przejdź do **Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)

3. Stwórz nowy projekt Google Cloud i wybierz go aby był aktywny
>[!TIP]
>Możesz sprawdzić dostępność kredytów OnRamp wybierając z menu po lewej stronie: Billing / Credits

4. Otwórz Cloud Shell ([dokumentacja](https://cloud.google.com/shell/docs))

5. Zweryfikuj konto które jest zalogowane w Cloud Shell
   ```bash
   gcloud auth list
   ```
>[!TIP]
>Jeżeli konto nie jest zalogowane, lub jest to inne konto niż to z dostępem do Twojego projektu Google Cloud, zaloguj się za pomocą komendy: `gcloud auth login`

6. Potwierdź, że wybrany jest odpowiedni projekt Google Cloud
   ```bash
   gcloud config get project
   ```
>[!TIP]
>Jeżeli projekt jest nieodpowiedni, zmień go za pomocą komendy: `gcloud config set project <ID_TWOJEGO_PROJEKTU>`

>[!CAUTION]
>Nie pomyl nazwy projektu z ID projektu! Nie zawsze są one takie same.

7. Sklonuj repozytorium z przykładowym kodem i przejdź do nowoutworzonego katalogu
   ```bash
   git clone https://github.com/avedave/eskadra-bielik-misja2
   ```

8. Przejdź do katalogu z kodem źródłowym
   ```bash
   cd eskadra-bielik-misja2
   ```

9. Uruchom edytor w katalogu z kodem źródłowym
   ```bash
   cloudshell workspace .
   ```

## 2. Konfiguracja zmiennych środowiskowych i usług Google Cloud

1. Przeanalizuj skrypt `setup_env.sh`

2. Otwórz ponownie terminal Cloud Shell

3. Uruchom skrypt `setup_env.sh`
   ```bash
   source setup_env.sh
   ```
>[!IMPORTANT]
>Jeżeli z jakiegoś powodu musisz ponownie uruchomić terminal Cloud Shell, pamiętaj aby ponownie uruchomić skrypt `setup_env.sh` aby wczytać zmienne środowiskowe.

4. Włącz potrzebne usługi w projekcie Google Cloud
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable bigquery.googleapis.com
   ```
5. Uzyskaj uprawnienia do wywoływania usług Cloud Run
   ```bash
   gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=user:$(gcloud config get-value account) \
    --role='roles/run.invoker'
   ```  

## 3. Uruchomienie modelu LLM Bielik na Cloud Run

1. Przeanalizuj skrypt `llm/cloud_run.sh`

2. Uruchom skrypt `llm/cloud_run.sh`
   ```bash
   cd llm
   ./cloud_run.sh
   ```
3. Sprawdź status usługi `bielik` w Cloud Console - Cloud Run - Services

4. Przeanalizuj plik `llm/llm_test1.sh` i zadaj pierwsze pytanie modelowi Bielik uruchamiając ten skrypt
   ```bash
   ./llm_test1.sh
   ```
5. Wróć do głównego katalogu projektu
   ```bash
   cd ..
   ```

## 4. Uruchomienie modelu embeddingowego EmbeddingGemma na Cloud Run

1. Przeanalizuj skrypt `embedding_model/cloud_run.sh`

2. Uruchom skrypt `embedding_model/cloud_run.sh`
   ```bash
   cd embedding_model
   ./cloud_run.sh
   ```
3. Sprawdź status usługi `embedding-gemma` w Cloud Console - Cloud Run - Services

4. Przeanalizuj plik `embedding_model/embedding_test1.sh` i wygeneruj pierwsze testowe embeddingi (wektory) dla przykładowego tekstu uruchamiając ten skrypt
   ```bash
   ./embedding_test1.sh
   ```
5. Wróć do głównego katalogu projektu
   ```bash
   cd ..
   ```

## 5. Inicjalizacja wektorowej bazy danych w BigQuery

Projekt wykorzystuje BigQuery z funkcją Vector Search jako bazę z wiedzą kontekstową.

1. Przejdź do katalogu `vector_store`
   ```bash
   cd vector_store
   ```

2. Zainstaluj wymagane biblioteki (w środowisku deweloperskim)
   ```bash
   pip install google-cloud-bigquery
   ```

3. Uruchom skrypt inicjalizacyjny, który stworzy zbiór danych i tabelę w BigQuery
   ```bash
   python init_db.py
   ```

4. Wróć do głównego katalogu projektu
   ```bash
   cd ..
   ```

## 6. Uruchomienie API (Orchestration) na Cloud Run

1. Przeanalizuj kod aplikacji FastAPI w katalogu `orchestration`

2. Przejdź do katalogu `orchestration`
   ```bash
   cd orchestration
   ```

3. Uruchom skrypt publikujący aplikację na Cloud Run
   ```bash
   ./cloud_run.sh
   ```

4. Po wdrożeniu gcloud wypisze adres URL usługi `orchestration-api`. Zapisz go do zmiennej środowiskowej
   ```bash
   export ORCHESTRATION_URL=$(gcloud run services describe orchestration-api --region $REGION --format="value(status.url)")
   ```

5. Wróć do głównego katalogu
   ```bash
   cd ..
   ```

## 7. Testowanie API - Zasilanie i Wyszukiwanie (RAG)

1. Zasil bazę BigQuery przykładowymi danymi z pliku CSV
   ```bash
   curl -X POST "$ORCHESTRATION_URL/ingest" \
        -F "file=@vector_store/hotel_rules.csv"
   ```

2. Sprawdź w Google Cloud Console -> BigQuery, czy rekordy pojawiły się w tabeli `rag_dataset.hotel_rules` 
   *(Proces indeksowania danych do Vector Search może chwilę potrwać, jednak dane tekstowe widoczne są natychmiast).*

3. Wykonaj testowe zapytanie wykorzystując RAG, dopytujące o informacje z wgranych reguł
   
   Pytanie o częstotliwość pomiaru chloru w basenie:
   ```bash
   curl -X POST "$ORCHESTRATION_URL/ask" \
        -H "Content-Type: application/json" \
        -d '{"query": "Jak często powinien być mierzony poziom chloru w basenie?"}'
   ```

   Pytanie o godzinę podawania śniadania:
   ```bash
   curl -X POST "$ORCHESTRATION_URL/ask" \
        -H "Content-Type: application/json" \
        -d '{"query": "O której godzinie jest podawane śniadanie?"}'
   ```
   
   Pytanie o parking:
   ```bash
   curl -X POST "$ORCHESTRATION_URL/ask" \
        -H "Content-Type: application/json" \
        -d '{"query": "Ile kosztuje parking hotelowy?"}'
   ```

## 8. Interfejs Programistyczny (API)

Aplikacja udostępnia proste API stworzone przy pomocy frameworka *FastAPI*, pozwalające nie tylko na zasilanie bazy wiedzy, ale również na zadawanie pytań.

Aplikacja definiuje w pliku `orchestration/main.py` następujące ścieżki:

* `GET /` – serwuje statyczny plik interfejsu użytkownika (`index.html`).
* `POST /ingest` – przyjmuje plik CSV i indeksuje zawarte w nim informacje jako wektory w BigQuery (wykorzystując model embeddingowy `EmbeddingGemma`).
* `POST /ask` – główny endpoint RAG: 
  - zamienia zapytanie z tekstu na wektor,
  - wyszukuje semantycznie 3 najbardziej zbliżone dokumenty wektorowe w tabeli BigQuery,
  - buduje prompt z odnalezionym kontekstem,
  - wysyła połączony prompt do modelu `Bielik` i zwraca ostateczną odpowiedź wraz z wybranym i wykorzystanym kontekstem.
* `POST /ask_direct` – służy jako zestawienie porównawcze (baseline). Przyjmuje zapytanie i wysyła je bezpośrednio do bazowego modelu `Bielik`, z całkowitym pominięciem RAG.

## 9. Interfejs Użytkownika (Web UI)

Oprócz interfejsu API, aplikacja udostępnia również prostą nakładkę WWW. Całość pozwala na wygodne sprawdzenie i porównanie działania bazowego modelu Bielik z modelem Bielik wspartym przez RAG.

Interfejs użytkownika zaimplementowano w jednym, statycznym pliku: `orchestration/static/index.html`. 

Skrypt osadzony w pliku HTML wysyła dwa jednoczesne żądania do endpointów `/ask` (wsparty RAG) oraz `/ask_direct` (bezpośrednio do modelu `Bielik`) i prezentuje obie odpowiedzi modelu obok siebie celem zilustrowania różnic. Wyświetla obok również jakich dokładnie fragmentów dokumentów BigQuery model użył w przypadku posiłkowania się dodatkowym kontekstem RAG.

> [!TIP]
> Zachęcamy Cię gorąco do eksperymentów! Przejrzyj dokładnie kod źródłowy plików `orchestration/main.py` oraz `orchestration/static/index.html`, aby zobaczyć, w jak prosty sposób w Pythonie łączy się wyszukiwanie wektorowe BigQuery z modelem LLM i serwuje dla prostej graficznej nakładki JavaScript. Spróbuj również zmodyfikować kod pliku `main.py`, aby polecić Bielikowi zachowywanie się jak pirat lub ekspert od IT w instrukcjach systemowych!

### Uruchomienie interfejsu

Aby otworzyć interfejs graficzny testowej aplikacji z poziomu Twojego projektu:

1. Wyświetl i kliknij w adres URL usługi `orchestration-api` uruchamiając w terminalu poniższą komendę:
   ```bash
   echo $ORCHESTRATION_URL
   ```
2. Po otwarciu opublikowanej strony w Twojej przeglądarce internetowej, wpisz w okno dialogowe dowolne zapytanie (np. "Do której godziny jest otwarty basen?") i kliknij "Zapytaj".
3. Porównaj strumień odpowiedzi wyświetlany dla samej bazy wiedzy modelu (bez dodatkowego kontekstu) z bogatszą odpowiedzią RAG wygenerowaną w oparciu o wiedzę z przeszukiwania BigQuery Vector Search.



