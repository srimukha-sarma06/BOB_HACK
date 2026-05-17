import json
import shutil
from pathlib import Path
from typing import Dict, Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_ROOT / "data"
REPOS_DIR = DATA_DIR / "repos"
META_DIR = DATA_DIR / "meta"
ARTIFACT_DIR = DATA_DIR / "artifacts"
VECTOR_DIR = DATA_DIR / "vectors"

for d in [DATA_DIR, REPOS_DIR, META_DIR, ARTIFACT_DIR, VECTOR_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def save_meta(repo_id: str, data: Dict[str, Any]) -> None:
    path = META_DIR / f"{repo_id}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_meta(repo_id: str) -> Dict[str, Any]:
    path = META_DIR / f"{repo_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No repo metadata found for {repo_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def repo_path(repo_id: str) -> Path:
    return REPOS_DIR / repo_id


def clean_repo(repo_id: str) -> None:
    path = repo_path(repo_id)
    if path.exists():
        shutil.rmtree(path)


def artifact_path(repo_id: str) -> Path:
    path = ARTIFACT_DIR / repo_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_artifact(repo_id: str, artifact_type: str, content: str) -> None:
    safe_name = "".join(c for c in artifact_type if c.isalnum() or c in "-_").strip() or "artifact"
    (artifact_path(repo_id) / f"{safe_name}.md").write_text(content, encoding="utf-8")


def load_artifacts(repo_id: str) -> Dict[str, str]:
    path = artifact_path(repo_id)
    artifacts = {}
    for file in sorted(path.glob("*.md")):
        artifacts[file.stem] = file.read_text(encoding="utf-8")
    return artifacts
