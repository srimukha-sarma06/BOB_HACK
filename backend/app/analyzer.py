from pathlib import Path
from typing import Any, Dict, List, Tuple

# Directories that should never be scanned. This keeps analysis fast and avoids junk.
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    ".next", ".cache", ".pytest_cache", ".mypy_cache", ".idea", ".vscode",
    "target", "out", "coverage", ".tox", ".turbo", ".parcel-cache",
}

LANG_BY_EXT = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".cu": "CUDA/C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".hh": "C++ Header",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "CSS",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bat": "Batch",
    ".csv": "CSV/Data",
    ".txt": "Text/Config",
}

CODE_EXTS = {
    ".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".cpp", ".cc",
    ".cxx", ".cu", ".c", ".h", ".hpp", ".hh", ".go", ".rs", ".rb", ".php",
    ".cs", ".swift", ".kt", ".html", ".css", ".scss", ".sql", ".sh", ".bat",
}

TEXT_EXTS = CODE_EXTS | {".md", ".rst", ".txt", ".json", ".yaml", ".yml", ".toml"}

DOC_NAMES = {
    "readme.md", "readme.txt", "contributing.md", "contributing.txt",
    "changelog.md", "changelog.txt", "license", "license.md", "license.txt",
    "docs.md", "docs.txt",
}

RISK_KEYWORDS = [
    "auth", "security", "payment", "billing", "db", "database", "migration",
    "crypto", "secret", "token", "permission", "password", "credential",
    "admin", "prod", "deploy",
]

ENTRYPOINT_NAMES = {
    # Python/backend
    "main.py", "app.py", "server.py", "manage.py", "wsgi.py", "asgi.py",

    # C/C++/CUDA
    "main.cpp", "main.cc", "main.cxx", "main.c", "main.cu",
    "app.cpp", "app.cc", "app.c", "server.cpp", "server.c",
    "deepstream_app.c", "deepstream_app.cpp", "deepstream-app.c", "deepstream-app.cpp",

    # Node/backend/frontend
    "index.js", "server.js", "main.js", "script.js", "app.js",

    # TypeScript
    "main.ts", "index.ts", "app.ts", "server.ts",

    # React/Vite/Next-style frontend
    "app.jsx", "app.tsx", "main.jsx", "main.tsx", "index.jsx", "index.tsx",
    "page.jsx", "page.tsx",

    # Static frontend
    "index.html",
}

CONFIG_NAMES = {
    "requirements.txt", "pyproject.toml", "package.json", "pnpm-lock.yaml",
    "yarn.lock", "package-lock.json", "dockerfile", "docker-compose.yml",
    ".env.example", "pytest.ini", "tsconfig.json", "vite.config.js",
    "vite.config.ts", "next.config.js", "tailwind.config.js", "go.mod",
    "cargo.toml", "pom.xml", "build.gradle", "cmakelists.txt", "makefile",
}

GENERATED_OR_VENDOR_HINTS = [
    "node_modules/",
    "dist/",
    "build/",
    "vendor/",
    "vendors/",
    "third_party/",
    "third-party/",
    "generated/",
    ".generated.",
    "bundle.js",
    "bundle.min.js",
    ".min.js",
    ".min.css",
    "wasm",
    ".bin.js",
    "packed_assets_loader",
    "hands_solution",
    "mediapipe",
]

ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".mp4", ".mp3",
    ".wav", ".pkl", ".pickle", ".pt", ".pth", ".onnx", ".h5", ".csv", ".wasm",
    ".bin", ".pdf", ".engine", ".weights",
}

CONFIG_HINTS = [
    "config", "cfg", "infer", "labels", "label", "model", "pipeline", "settings",
    "params", "parameters", "properties", "cmakelists",
]

ML_ASSET_HINTS = [
    "model", "weights", "labels", "engine", "onnx", "pkl", "pickle", "dataset",
    "sample", "assets",
]


def path_has_part(path: Path, names: set[str]) -> bool:
    return any(part in names for part in path.parts)


def iter_files(repo_path: Path) -> List[Path]:
    files: List[Path] = []

    for p in repo_path.rglob("*"):
        if path_has_part(p, IGNORE_DIRS):
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


def looks_generated_or_vendor(path: str) -> bool:
    lower = path.lower()
    return any(hint in lower for hint in GENERATED_OR_VENDOR_HINTS)


def is_config_file(file: Path, relative_path: str) -> bool:
    lower = relative_path.lower()
    name = file.name.lower()

    if name in CONFIG_NAMES:
        return True

    if file.suffix.lower() in {".yaml", ".yml", ".json", ".toml"}:
        return True

    if file.suffix.lower() == ".txt" and any(hint in lower for hint in CONFIG_HINTS):
        return True

    return False


def is_documentation_file(file: Path, relative_path: str) -> bool:
    lower = relative_path.lower()
    name = file.name.lower()

    if name in DOC_NAMES:
        return True

    if lower.startswith("docs/") and file.suffix.lower() in {".md", ".rst", ".txt"}:
        return True

    if file.suffix.lower() in {".md", ".rst"} and not is_config_file(file, relative_path):
        return True

    return False


def is_asset_file(file: Path, relative_path: str) -> bool:
    lower = relative_path.lower()
    ext = file.suffix.lower()

    if ext in ASSET_EXTS:
        return True

    if lower.startswith("assets/") and not is_documentation_file(file, relative_path):
        return True

    if any(hint in lower for hint in ML_ASSET_HINTS) and ext not in CODE_EXTS:
        return True

    return False


def detect_package_manager(files: List[str]) -> str:
    names = {Path(f).name.lower() for f in files}

    checks = [
        ("cmakelists.txt", "C/C++ / CMake"),
        ("makefile", "C/C++ / Makefile"),
        ("pyproject.toml", "Python / pyproject.toml"),
        ("requirements.txt", "Python / requirements.txt"),
        ("pipfile", "Python / Pipenv"),
        ("environment.yml", "Conda / environment.yml"),
        ("package.json", "Node / package.json"),
        ("pnpm-lock.yaml", "Node / pnpm"),
        ("yarn.lock", "Node / yarn"),
        ("package-lock.json", "Node / npm"),
        ("pom.xml", "Java / Maven"),
        ("build.gradle", "Java / Gradle"),
        ("cargo.toml", "Rust / Cargo"),
        ("go.mod", "Go modules"),
    ]

    for filename, label in checks:
        if filename in names:
            return label

    return "Unknown"


def find_entrypoints(repo_path: Path, files: List[Path]) -> List[str]:
    candidates: List[str] = []

    for file in files:
        r = rel(repo_path, file)
        name = file.name.lower()
        lower = r.lower()

        if looks_generated_or_vendor(lower):
            continue

        if name in ENTRYPOINT_NAMES:
            candidates.append(r)
            continue

        if lower in {
            "src/index.js", "src/index.ts", "src/main.js", "src/main.ts",
            "src/main.jsx", "src/main.tsx", "src/main.cpp", "src/main.c",
            "src/main.cc", "src/main.cu",
        }:
            candidates.append(r)

    return candidates[:12]


def score_file(repo_path: Path, file: Path, test_files: List[str]) -> Tuple[int, str, bool]:
    r = rel(repo_path, file)
    lower = r.lower()
    name = file.name.lower()
    ext = file.suffix.lower()
    text = safe_read(file, 30_000)
    text_lower = text.lower()
    lines = text.splitlines()

    score = 50
    reasons: List[str] = []

    generated_or_vendor = looks_generated_or_vendor(lower)
    asset_file = is_asset_file(file, lower)
    docs_file = is_documentation_file(file, lower)
    config_file = is_config_file(file, lower)

    if generated_or_vendor:
        score -= 40
        reasons.append("likely generated/vendor file")

    if asset_file:
        score -= 18
        reasons.append("asset/model/data file")

    if docs_file:
        score += 18
        reasons.append("documentation is safe for a first contribution")

    if config_file:
        score += 4
        reasons.append("configuration/build file")

    if name in ENTRYPOINT_NAMES:
        score += 18
        reasons.append("main project entrypoint")

    if ext == ".py" and "/" not in r:
        score += 10
        reasons.append("top-level Python script")

    if ext in {".cpp", ".cc", ".cxx", ".c", ".cu", ".h", ".hpp", ".hh"}:
        score += 6
        reasons.append("editable C/C++ source file")

    if ext in {".html", ".css", ".js", ".jsx", ".ts", ".tsx"} and not generated_or_vendor:
        score += 8
        reasons.append("editable frontend file")

    if "todo" in text_lower or "fixme" in text_lower:
        score += 16
        reasons.append("contains TODO/FIXME")

    if 1 <= len(lines) < 160:
        score += 12
        reasons.append("small file")

    if len(lines) > 500:
        score -= 18
        reasons.append("large file")

    if any(k in lower for k in ["route", "controller", "handler", "view", "component", "page", "pipeline"]):
        score += 8
        reasons.append("feature-level file")

    if any(k in lower for k in RISK_KEYWORDS):
        score -= 28
        reasons.append("risk-sensitive area")

    if ext in CODE_EXTS:
        import_count = sum(
            1
            for line in lines
            if line.strip().startswith((
                "import ", "from ", "require(", "const ", "let ", "var ",
                "#include", "using namespace",
            ))
        )

        if import_count > 25:
            score -= 12
            reasons.append("many imports/includes/dependencies")

    stem = file.stem.lower()

    if any(stem in tf.lower() for tf in test_files):
        score += 14
        reasons.append("nearby test exists")

    # .txt label/config files are useful context, but should not dominate Good First Files.
    if ext == ".txt" and (config_file or asset_file) and not docs_file:
        score = min(score, 58)
        reasons.append("not a primary edit target")

    score = max(0, min(100, score))

    is_risky = (
        generated_or_vendor
        or any(k in lower for k in RISK_KEYWORDS)
        or score < 35
    )

    return score, "; ".join(reasons) or "general project file", is_risky


def group_files(repo_path: Path, files: List[Path]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {
        "entrypoints": [],
        "source": [],
        "frontend": [],
        "scripts": [],
        "routes": [],
        "tests": [],
        "docs": [],
        "config": [],
        "assets": [],
    }

    for file in files:
        r = rel(repo_path, file)
        lower = r.lower()
        name = file.name.lower()
        ext = file.suffix.lower()

        if looks_generated_or_vendor(lower):
            if is_asset_file(file, lower):
                groups["assets"].append(r)
            continue

        if name in ENTRYPOINT_NAMES:
            groups["entrypoints"].append(r)

        if ext in {".cpp", ".cc", ".cxx", ".cu", ".c", ".h", ".hpp", ".hh", ".java", ".go", ".rs", ".cs"}:
            groups["source"].append(r)

        if ext in {".html", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx"}:
            groups["frontend"].append(r)

        if ext in {".py", ".sh", ".bat"}:
            groups["scripts"].append(r)

        if any(k in lower for k in ["route", "controller", "handler", "api"]):
            groups["routes"].append(r)

        if "test" in lower or "spec" in lower:
            groups["tests"].append(r)

        if is_documentation_file(file, lower):
            groups["docs"].append(r)

        if is_config_file(file, lower):
            groups["config"].append(r)

        if is_asset_file(file, lower):
            groups["assets"].append(r)

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

        if ext in TEXT_EXTS:
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
        for f, r in zip(files, rel_files)
        if is_documentation_file(f, r)
    ]

    entrypoints = find_entrypoints(repo_path, files)
    package_manager = detect_package_manager(rel_files)

    scored: List[Dict[str, Any]] = []
    risky: List[Dict[str, Any]] = []

    for file in files:
        r = rel(repo_path, file)

        if file.suffix.lower() not in TEXT_EXTS and file.suffix.lower() not in ASSET_EXTS:
            continue

        score, reason, is_risky = score_file(repo_path, file, test_files)

        item = {
            "file": r,
            "score": score,
            "reason": reason,
        }

        if is_risky:
            risky.append(item)
        else:
            scored.append(item)

    all_good_first_files = sorted(scored, key=lambda x: x["score"], reverse=True)
    all_risky_files = sorted(risky, key=lambda x: (x["score"], x["file"]))

    good_first_files = all_good_first_files[:8]
    risky_files = all_risky_files[:8]

    code_files = [
        f
        for f in files
        if f.suffix.lower() in CODE_EXTS and not looks_generated_or_vendor(rel(repo_path, f).lower())
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
    risky_penalty = min(1.0, risky_count / max(1, code_file_count * 0.18))

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

    if not test_files:
        onboarding_score -= 14

    if readme_exists and not test_files and docs_count <= 1:
        onboarding_score -= 6

    if entrypoint_count > 0 and not test_files:
        onboarding_score += 4

    onboarding_score = max(5, min(100, onboarding_score))

    estimated_manual = (
        45
        + int(total_file_count * 1.4)
        + int(code_file_count * 1.8)
        + (0 if readme_exists else 50)
        + (0 if test_files else 60)
        + int(risky_count * 5)
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
    lines: List[str] = []

    for file in sorted(files, key=lambda p: rel(repo_path, p))[:max_lines]:
        lines.append(rel(repo_path, file))

    if len(files) > max_lines:
        lines.append(f"... and {len(files) - max_lines} more files")

    return "\n".join(lines)
