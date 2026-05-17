from pathlib import Path
from typing import Dict, List, Any, Tuple

IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    ".next", ".cache", ".pytest_cache", ".mypy_cache", ".idea", ".vscode",
    "target", "out", "coverage", ".tox"
}

LANG_BY_EXT = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".md": "Markdown",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".html": "HTML",
    ".css": "CSS",
}

CODE_EXTS = set(LANG_BY_EXT) - {".md", ".json", ".yaml", ".yml"}
DOC_NAMES = {"README.md", "CONTRIBUTING.md", "CHANGELOG.md", "docs"}

RISK_KEYWORDS = [
    "auth",
    "security",
    "payment",
    "billing",
    "db",
    "database",
    "migration",
    "crypto",
    "secret",
    "token",
    "permission",
]


def iter_files(repo_path: Path) -> List[Path]:
    files = []

    for p in repo_path.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue

        if p.is_file():
            try:
                if p.stat().st_size > 500_000:
                    continue
            except OSError:
                continue

            files.append(p)

    return files


def rel(repo_path: Path, file: Path) -> str:
    return str(file.relative_to(repo_path)).replace("\\", "/")


def safe_read(file: Path, max_chars: int = 200_000) -> str:
    try:
        return file.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def detect_package_manager(files: List[str]) -> str:
    names = set(files)

    checks = [
        ("pyproject.toml", "Python / pyproject.toml"),
        ("requirements.txt", "Python / requirements.txt"),
        ("Pipfile", "Python / Pipenv"),
        ("environment.yml", "Conda / environment.yml"),
        ("package.json", "Node / package.json"),
        ("pnpm-lock.yaml", "Node / pnpm"),
        ("yarn.lock", "Node / yarn"),
        ("pom.xml", "Java / Maven"),
        ("build.gradle", "Java / Gradle"),
        ("Cargo.toml", "Rust / Cargo"),
        ("go.mod", "Go modules"),
    ]

    for filename, label in checks:
        if filename in names:
            return label

    return "Unknown"


def find_entrypoints(repo_path: Path, files: List[Path]) -> List[str]:
    candidates = []

    names = {
        "main.py",
        "app.py",
        "server.py",
        "index.js",
        "server.js",
        "main.ts",
        "index.ts",
        "App.jsx",
        "App.tsx",
    }

    for file in files:
        r = rel(repo_path, file)
        if file.name in names:
            candidates.append(r)

    return candidates[:12]


def score_file(repo_path: Path, file: Path, test_files: List[str]) -> Tuple[int, str, bool]:
    r = rel(repo_path, file)
    lower = r.lower()
    text = safe_read(file, 30_000)
    lines = text.splitlines()

    score = 50
    reasons = []

    if file.suffix.lower() in [".md", ".txt"]:
        score += 18
        reasons.append("docs file is safe for a first contribution")

    if "todo" in text.lower() or "fixme" in text.lower():
        score += 16
        reasons.append("contains TODO/FIXME")

    if len(lines) < 160:
        score += 12
        reasons.append("small file")

    if len(lines) > 500:
        score -= 18
        reasons.append("large file")

    if any(k in lower for k in ["route", "controller", "handler", "view"]):
        score += 8
        reasons.append("feature-level file")

    if any(k in lower for k in RISK_KEYWORDS):
        score -= 28
        reasons.append("risk-sensitive area")

    if file.suffix.lower() in CODE_EXTS:
        import_count = sum(
            1
            for line in lines
            if line.strip().startswith(("import ", "from ", "require(", "const "))
        )

        if import_count > 18:
            score -= 12
            reasons.append("many imports/dependencies")

    stem = file.stem.lower()

    if any(stem in tf.lower() for tf in test_files):
        score += 14
        reasons.append("nearby test exists")

    score = max(0, min(100, score))

    is_risky = any(k in lower for k in RISK_KEYWORDS) or score < 35

    return score, "; ".join(reasons) or "general project file", is_risky


def group_files(repo_path: Path, files: List[Path]) -> Dict[str, List[str]]:
    groups = {
        "entrypoints": [],
        "routes": [],
        "tests": [],
        "docs": [],
        "config": [],
    }

    for file in files:
        r = rel(repo_path, file)
        lower = r.lower()

        if file.name.lower() in {
            "main.py",
            "app.py",
            "server.py",
            "index.js",
            "main.ts",
            "app.jsx",
            "app.tsx",
        }:
            groups["entrypoints"].append(r)

        if any(k in lower for k in ["route", "controller", "handler", "api"]):
            groups["routes"].append(r)

        if "test" in lower or "spec" in lower:
            groups["tests"].append(r)

        if file.suffix.lower() in [".md", ".rst"] or "docs/" in lower:
            groups["docs"].append(r)

        if file.name.lower() in {
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "dockerfile",
            ".env.example",
            "pytest.ini",
            "tsconfig.json",
            "vite.config.js",
        }:
            groups["config"].append(r)

    return {k: v[:12] for k, v in groups.items()}


def analyze_repo(repo_path: Path, repo_id: str, repo_name: str, repo_url: str) -> Dict[str, Any]:
    files = iter_files(repo_path)
    rel_files = [rel(repo_path, f) for f in files]

    languages: Dict[str, int] = {}
    todo_count = 0

    for file in files:
        ext = file.suffix.lower()
        lang = LANG_BY_EXT.get(ext)

        if lang:
            languages[lang] = languages.get(lang, 0) + 1

        if ext in CODE_EXTS or ext in {".md", ".txt"}:
            text = safe_read(file, 200_000).lower()
            todo_count += text.count("todo") + text.count("fixme")

    readme_exists = any(f.name.lower() == "readme.md" for f in files)

    test_files = [
        r
        for r in rel_files
        if "test" in r.lower() or "spec" in r.lower()
    ]

    docs = [
        r
        for r in rel_files
        if r.lower().endswith((".md", ".rst")) or r.lower().startswith("docs/")
    ]

    entrypoints = find_entrypoints(repo_path, files)
    package_manager = detect_package_manager([Path(r).name for r in rel_files])

    scored = []
    risky = []

    for file in files:
        if file.suffix.lower() not in CODE_EXTS and file.suffix.lower() not in [".md", ".txt"]:
            continue

        score, reason, is_risky = score_file(repo_path, file, test_files)

        item = {
            "file": rel(repo_path, file),
            "score": score,
            "reason": reason,
        }

        if is_risky:
            risky.append(
                {
                    "file": item["file"],
                    "reason": reason,
                    "score": score,
                }
            )
        else:
            scored.append(item)

    # Keep full lists for scoring.
    all_good_first_files = sorted(scored, key=lambda x: x["score"], reverse=True)
    all_risky_files = sorted(risky, key=lambda x: x.get("file", ""))

    # Only slice for frontend display.
    good_first_files = all_good_first_files[:8]
    risky_files = all_risky_files[:8]

    # More nuanced repo-level onboarding score.
    # This is still heuristic, but now different repos get meaningfully different scores.
    code_files = [
        f
        for f in files
        if f.suffix.lower() in CODE_EXTS
    ]

    total_file_count = max(1, len(files))
    code_file_count = max(1, len(code_files))
    test_count = len(test_files)
    docs_count = len(docs)
    entrypoint_count = len(entrypoints)
    good_first_count = len(all_good_first_files)
    risky_count = len(all_risky_files)

    test_ratio = min(1.0, test_count / max(1, code_file_count * 0.25))
    docs_ratio = min(1.0, docs_count / max(1, total_file_count * 0.08))
    entrypoint_score = min(1.0, entrypoint_count / 3)
    good_first_score = min(1.0, good_first_count / 5)
    risky_penalty = min(1.0, risky_count / max(1, code_file_count * 0.12))

    size_penalty = 0

    if total_file_count > 100:
        size_penalty += 5

    if total_file_count > 300:
        size_penalty += 8

    if total_file_count > 700:
        size_penalty += 12

    language_penalty = 0

    if len(languages) > 4:
        language_penalty += 5

    if len(languages) > 7:
        language_penalty += 5

    onboarding_score = 30

    if readme_exists:
        onboarding_score += 10

    onboarding_score += int(18 * test_ratio)
    onboarding_score += int(14 * docs_ratio)
    onboarding_score += int(10 * entrypoint_score)
    onboarding_score += int(12 * good_first_score)

    if todo_count > 0:
        onboarding_score += min(8, todo_count)

    onboarding_score -= int(16 * risky_penalty)
    onboarding_score -= size_penalty
    onboarding_score -= language_penalty

    # If there are no tests, heavily punish onboarding confidence.
    if not test_files:
        onboarding_score -= 14

    # If README exists but no tests/docs, don't over-reward README alone.
    if readme_exists and not test_files and docs_count <= 1:
        onboarding_score -= 6

    onboarding_score = max(5, min(100, onboarding_score))

    # Time estimate now varies more across repos.
    estimated_manual = (
        45
        + int(total_file_count * 1.4)
        + int(code_file_count * 1.8)
        + (0 if readme_exists else 50)
        + (0 if test_files else 60)
        + int(risky_count * 6)
        + int(len(languages) * 8)
    )

    estimated_firstpr = max(
        15,
        int(estimated_manual * (0.18 if onboarding_score >= 70 else 0.28)),
    )

    return {
        "repo_id": repo_id,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "total_files": len(files),
        "languages": languages or {"Unknown": len(files)},
        "readme_exists": readme_exists,
        "test_files": test_files[:20],
        "entrypoints": entrypoints[:20],
        "docs": docs[:20],
        "todo_count": todo_count,
        "package_manager": package_manager,
        "risky_files": risky_files,
        "good_first_files": good_first_files,
        "file_groups": group_files(repo_path, files),
        "onboarding_score": onboarding_score,
        "estimated_manual_minutes": estimated_manual,
        "estimated_firstpr_minutes": estimated_firstpr,
    }


def build_tree_preview(repo_path: Path, max_lines: int = 160) -> str:
    files = iter_files(repo_path)
    lines = []

    for file in sorted(files, key=lambda p: rel(repo_path, p))[:max_lines]:
        lines.append(rel(repo_path, file))

    if len(files) > max_lines:
        lines.append(f"... and {len(files) - max_lines} more files")

    return "\n".join(lines)
