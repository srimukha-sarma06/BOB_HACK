from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AnalyzeRequest, SemanticSearchRequest, ArtifactRequest
from .repo_utils import make_repo_id, clone_or_copy_repo, slugify
from .storage import save_meta, load_meta, repo_path, clean_repo, save_artifact, load_artifacts, PROJECT_ROOT
from .analyzer import analyze_repo, build_tree_preview
from .vector_store import get_vector_store
from .bob_prompts import generate_bob_prompts
from .llm import generate_architecture_summary

app = FastAPI(title="FirstPR Academy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = get_vector_store()


@app.get("/")
def root():
    return {
        "name": "FirstPR Academy API",
        "status": "running",
        "vector_backend": vector_store.backend_name,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "vector_backend": vector_store.backend_name}


def analyze_from_link(repo_link: str, repo_name: str = "", repo_description: str = "") -> Dict[str, Any]:
    repo_name = repo_name or slugify(repo_link)
    repo_id = make_repo_id(repo_link, repo_name)
    target = repo_path(repo_id)

    try:
        source_type, local_path = clone_or_copy_repo(repo_link, target)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not clone/copy repo: {exc}")

    analysis = analyze_repo(target, repo_id=repo_id, repo_name=repo_name, repo_url=repo_link)
    analysis["repo_description"] = repo_description
    analysis["source_type"] = source_type
    analysis["local_path"] = local_path

    try:
        vector_info = vector_store.build(repo_id, target)
    except Exception as exc:
        vector_info = {"backend": vector_store.backend_name, "chunks_indexed": 0, "error": str(exc)}
    analysis["vector_index"] = vector_info
    analysis["vector_index_ready"] = vector_info.get("chunks_indexed", 0) > 0

    tree_preview = build_tree_preview(target)
    analysis["architecture_summary"] = generate_architecture_summary(analysis, tree_preview)
    analysis["bob_prompts"] = generate_bob_prompts(analysis)

    save_meta(repo_id, analysis)
    save_artifact(repo_id, "01-static-analysis", "```json\n" + __import__("json").dumps(analysis, indent=2) + "\n```")
    save_artifact(repo_id, "02-architecture-summary", analysis["architecture_summary"])
    for name, prompt in analysis["bob_prompts"].items():
        save_artifact(repo_id, f"bob-prompt-{name}", prompt)

    return analysis


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    repo_link = req.repo_link or req.repo_url
    if not repo_link:
        raise HTTPException(status_code=422, detail="Provide repo_link or repo_url")
    return analyze_from_link(repo_link, req.repo_name or "", req.repo_description or "")


@app.post("/analyze-sample")
def analyze_sample():
    sample = PROJECT_ROOT / "sample-repos" / "broken-task-api"
    if not sample.exists():
        raise HTTPException(status_code=500, detail=f"Sample repo not found at {sample}")
    return analyze_from_link(str(sample), "broken-task-api", "Local sample repo with intentional first-PR issues")


@app.get("/repos/{repo_id}/summary")
def repo_summary(repo_id: str):
    try:
        return load_meta(repo_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repo not found")


@app.get("/repos/{repo_id}/bob-prompts")
def repo_bob_prompts(repo_id: str):
    try:
        meta = load_meta(repo_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repo not found")
    return meta.get("bob_prompts", generate_bob_prompts(meta))


@app.post("/repos/{repo_id}/semantic-search")
def semantic_search(repo_id: str, req: SemanticSearchRequest):
    try:
        load_meta(repo_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repo not found")
    results = vector_store.query(repo_id, req.query, req.top_k)
    return {
        "repo_id": repo_id,
        "query": req.query,
        "top_k": req.top_k,
        "vector_backend": vector_store.backend_name,
        "results": results,
    }


@app.post("/repos/{repo_id}/artifacts")
def post_artifact(repo_id: str, req: ArtifactRequest):
    try:
        load_meta(repo_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repo not found")
    save_artifact(repo_id, req.artifact_type, req.content)
    return {"ok": True, "repo_id": repo_id, "artifact_type": req.artifact_type}


@app.get("/repos/{repo_id}/artifacts")
def get_artifacts(repo_id: str):
    try:
        load_meta(repo_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Repo not found")
    return {"repo_id": repo_id, "artifacts": load_artifacts(repo_id)}
