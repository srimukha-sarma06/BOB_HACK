# FirstPR Academy

**FirstPR Academy** is a Bob-powered developer onboarding product for hackathons.

It turns an unfamiliar GitHub repo into:

1. a beginner-friendly repo map,
2. a Good First PR score,
3. real vector-search over repository chunks,
4. Bob-ready prompts,
5. Bob artifact storage,
6. a final submission dashboard.

The visual style is a premium wizard-academy theme, but it uses original names and styling.

---

## What is complete in this zip?

### Backend

- FastAPI backend
- GitHub repo cloning
- Local sample repo analysis
- Static repo analyzer
- Good First PR scoring
- Local vector store
- Optional ChromaDB vector backend
- Semantic repo search endpoint
- Bob prompt generation
- Bob artifact save/load endpoints
- Optional Groq/OpenAI-compatible architecture summary
- No PostgreSQL required

### Frontend

- React + Vite frontend
- No Tailwind setup required
- Beautiful custom CSS
- Repo upload screen
- Repo overview dashboard
- Repo map
- Real vector search tab
- Bob missions tab
- Bob artifact vault
- Submission checklist

### Submission material

- Demo script
- Bob report template
- Bob prompts
- Sample repo

---

## Quick start

Open two terminals.

### Terminal 1: backend

#### Windows

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Linux / macOS

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend docs:

```txt
http://127.0.0.1:8000/docs
```

### Terminal 2: frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```txt
http://127.0.0.1:5173
```

---

## Optional LLM summary

The app works without an API key.

If you want Groq/OpenAI-compatible architecture summaries, create:

```txt
backend/.env
```

Then add:

```env
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

or:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

---

## Vector DB details

The backend includes two vector modes:

1. **ChromaDB mode** if `chromadb` is installed correctly.
2. **Built-in local vector store fallback** using hashed embeddings + cosine similarity.

This means the project still runs even if ChromaDB has dependency issues.

Semantic search endpoint:

```txt
POST /repos/{repo_id}/semantic-search
```

Example body:

```json
{
  "query": "where should I add email validation?",
  "top_k": 5
}
```

---

## How IBM Bob is used

This project is intentionally designed to make Bob usage visible.

Bob is used for:

1. repo understanding,
2. architecture explanation,
3. safe first-task selection,
4. implementation planning,
5. test generation,
6. PR summary generation,
7. final Bob report export.

The app generates Bob-ready missions. During the hackathon demo, open the repo in IBM Bob, paste the generated missions, let Bob act on the repo, then paste/export Bob outputs into the Artifact Vault.

---

## Demo flow

1. Start backend and frontend.
2. Click **Use sample repo** or paste a GitHub URL.
3. Show the Overview score.
4. Show the Repo Map.
5. Search in Vector Search:  
   `where should I add email validation?`
6. Open Bob Missions.
7. Copy the prompts into IBM Bob.
8. Paste Bob outputs into the Artifact Vault.
9. Show the final checklist.

---

## Important honest note

This zip gives you the full runnable project, including vector search and artifact management.  
But I cannot export an official IBM Bob report from your account. You must do that during the hackathon using IBM Bob and attach it to your submission if required.
