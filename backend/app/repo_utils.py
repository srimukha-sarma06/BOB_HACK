import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Tuple
from git import Repo


def slugify(text: str) -> str:
    text = text.strip().replace("\\", "/").rstrip("/")
    name = text.split("/")[-1] or "repo"
    if name.endswith(".git"):
        name = name[:-4]
    cleaned = []
    for ch in name.lower():
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in "-_.":
            cleaned.append(ch)
        else:
            cleaned.append("-")
    return "".join(cleaned).strip("-") or "repo"


def make_repo_id(repo_link: str, repo_name: str = "") -> str:
    raw = f"{repo_link}|{repo_name}"
    h = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    return f"{slugify(repo_name or repo_link)}-{h}"


def clone_or_copy_repo(repo_link: str, target_dir: Path) -> Tuple[str, str]:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    maybe_local = Path(repo_link).expanduser()
    if maybe_local.exists():
        shutil.copytree(maybe_local, target_dir, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv", "node_modules"))
        return "local-copy", str(target_dir)

    try:
        Repo.clone_from(repo_link, target_dir, depth=1)
        return "gitpython", str(target_dir)
    except Exception:
        # fallback to subprocess git clone because some environments behave better with CLI git
        subprocess.run(["git", "clone", "--depth", "1", repo_link, str(target_dir)], check=True, timeout=120)
        return "git-cli", str(target_dir)
