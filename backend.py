from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from git import Repo
from openai import OpenAI

import tempfile
import os
import shutil

from app.database import Base, engine, SessionLocal
from app.models import RepoStorage
from app.schema import RepoCreate, RepoOutput

router = APIRouter()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Client will safely extract the key loaded into the environment by backend_app.py
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)


@router.post(
    "/analyze",
    status_code=status.HTTP_201_CREATED,
    response_model=RepoOutput
)
def create_repo_output(
    data: RepoCreate,
    db: Session = Depends(get_db)
):
    temp_dir = tempfile.mkdtemp()
    try:
        # Crucial: Force Git to throw an error instantly instead of hanging on hidden authorization requests
        os.environ["GIT_TERMINAL_PROMPT"] = "0"

        # Clone repo with depth=1 (shallow clone) to drastically lower download time
        repo = Repo.clone_from(
            data.repo_link,
            temp_dir,
            depth=1
        )

        repo_files = []
        readme_content = "No README found."

        # Basic repo structure extraction
        for root, dirs, files in os.walk(temp_dir):
            # Ignore heavy folders and standard configuration noise
            dirs[:] = [
                d for d in dirs
                if d not in [".git", "node_modules", "venv", "__pycache__", ".github", "logs", "checkpoints", "runs"]
            ]

            for file in files:
                if len(repo_files) >= 200:
                    break
                
                rel_path = os.path.relpath(os.path.join(root, file), temp_dir)
                repo_files.append(rel_path)
                
                # Snag README context to feed high-level context to Bob
                if file.lower() == "readme.md" and readme_content == "No README found.":
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            readme_content = f.read()[:2000]
                    except Exception:
                        pass

            if len(repo_files) >= 200:
                break

        repo_tree = "\n".join(repo_files)

        # LLM architecture summary utilizing correct OpenAI string model
        llm_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Bob, an expert senior software architect. "
                        "Your job is to onboard new developers smoothly by lowering the Time-to-First-PR."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Analyze this repository structure and context.

Repository Name: {data.repo_name}
Description: {data.repo_description}

---
README Snippet:
{readme_content}
---

Repository File Tree (Subset):
{repo_tree}

Explain clearly:
1. What this repo does & its core architecture.
2. The most critical files a engineer must look at first.
3. Suggest 2 actionable "Good First Issues" (e.g., adding an endpoint, fixing a minor edge-case logic flaw, or creating specific unit tests) that a newcomer can do immediately to secure their first PR.
"""
                }
            ]
        )

        architecture_summary = llm_response.choices[0].message.content

        # Save to DB
        new_repo = RepoStorage(
            repo_link=data.repo_link,
            repo_name=data.repo_name,
            repo_description=data.repo_description,
            architecture_summary=architecture_summary
        )

        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)

        return new_repo

    except Exception as e:
        import traceback
        print("\n=== BACKEND CRASH STACK TRACE ===")
        traceback.print_exc()
        print("=================================\n")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
    finally:
        # Crucial clean-up to prevent filling up server storage space
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)