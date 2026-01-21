# Proiect-BDNSV-Veisa-Radu


# Semantic Search Engine with RAG

Aceasta aplicatie este un motor de cautare semantic care indexeaza documente PDF, 
permite cautarea bazata pe sens (nu doar pe cuvinte cheie) si integreaza un LLM (Llama 3 via Groq) 
pentru a raspunde la intrebari pe baza continutului gasit (RAG - Retrieval-Augmented Generation).

## Tehnologii Utilizate

* **Backend:** Python, FastAPI, FAISS (Vector Database), LangChain, SentenceTransformers.
* **Frontend:** React.js, Vite, Axios.
* **LLM:** Llama 3.1 (via Groq API).

## Ghid de Instalare

### 1. Clonarea Proiectului

### 2. Setup environment in backend 
- rulare python -m venv venv su venv\Scripts\activate in backend

### 3. Instalare dependinte
- pip install -r requirements.txt

### 4. Configurare .env
- USE_LOCAL_LLM=false
- GROQ_API_KEY=cheie pt grok

Rulare backend: python main.py

### 5. Instalare dependinte frontend
- npm install

Rulare frontend: npm run dev

