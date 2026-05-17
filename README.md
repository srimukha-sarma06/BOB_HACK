# FirstPR Academy

FirstPR Academy is a Bob-powered developer onboarding product.

## The Problem

New contributors waste 2-4 hours understanding unfamiliar repositories before making their first safe pull request. They struggle to:
- Identify which files are safe to edit
- Understand the codebase architecture
- Find good first contribution opportunities
- Avoid breaking critical systems

FirstPR Academy solves this with AI-powered static analysis and IBM Bob guidance.

## The Solution

It turns an unfamiliar repository into:

1. a beginner-friendly repo map,
2. a Good First PR score,
3. semantic repo search,
4. IBM Bob mission prompts,
5. a Bob artifact vault,
6. a submission-ready demo workflow.

The core idea:

> Unknown repo → safe mission → tested PR.

---

## What is fixed in this version

- Handles Python, JavaScript, TypeScript, static web, C/C++, CUDA, CMake, and ML-style repos better.
- Detects entrypoints such as `index.html`, `script.js`, `main.py`, `main.cpp`, `main.c`, `main.cu`, and DeepStream-style app files.
- Does not treat random `.txt` config/model label files as documentation.
- Penalizes assets, generated files, model/data files, and vendor/WASM files.
- Skips junk files in semantic search.
- Vector search scores are normalized to a clean 0-1 range.
- Vite is pinned to a Node 18-compatible version.

---

## Required keys

For the core app:

```txt
No API key is required.
```

These work without keys:

- repo scanning
- scoring
- vector search
- sample repo demo
- Bob prompt generation
- artifact vault
- public GitHub repos

---

## Optional keys

Create:

```txt
backend/.env
```

Use this:

```env
# Optional richer architecture summaries
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Optional OpenAI alternative
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini

# Optional private GitHub repo analysis
GITHUB_TOKEN=your_github_pat_here
```

ChromaDB is local. It does not need an API key.

**Important**: IBM Bob is used through the IBM Bob IDE (external tool), not embedded in this app. You copy prompts from FirstPR Academy's "Bob Missions" tab and paste them into IBM Bob IDE, then paste Bob's responses back into the "Artifacts" tab for your submission.

---

## Run backend with conda

```bash
cd backend
conda activate firstpr
pip install -r requirements.txt
rm -rf data
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```txt
http://127.0.0.1:8000/docs
```

---

## Run frontend

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

Open:

```txt
http://127.0.0.1:5173
```

---

## Test flow

1. Start backend.
2. Start frontend.
3. Click **Use sample repo instead**.
4. Open **Overview**.
5. Open **Repo Map**.
6. Open **Vector Search** and try:
   - `where should I add email validation?`
   - `where is the main entry point?`
   - `where is model inference handled?`
7. Open **Bob Missions**.
8. Copy the prompts into IBM Bob.
9. Paste Bob outputs into **Artifacts**.

---

## IBM Bob submission flow

Use IBM Bob IDE and export Bob task/session history files.

Add them to:

```txt
bob_sessions/
```

Also save useful outputs in:

```txt
submission/
```

Suggested files:

```txt
submission/bob-project-review.md
submission/bob-output-architecture.md
submission/bob-output-task-selection.md
submission/bob-output-implementation-plan.md
submission/bob-output-pr-summary.md

bob_sessions/exported-bob-task-history-1.md
bob_sessions/exported-bob-task-history-1-consumption.png
```

Do not commit real API keys or `.env`.
