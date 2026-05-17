import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .storage import VECTOR_DIR
from .analyzer import iter_files, rel, safe_read

VECTOR_DIM = 384

INDEXABLE_EXTS = {
    ".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".cpp",
    ".cc", ".cxx", ".cu", ".c", ".h", ".hpp", ".hh", ".go", ".rs", ".rb",
    ".php", ".cs", ".md", ".rst", ".txt", ".yaml", ".yml", ".json", ".toml",
    ".html", ".css", ".scss",
}

SKIP_PATH_HINTS = [
    "node_modules/",
    ".git/",
    ".venv/",
    "venv/",
    "dist/",
    "build/",
    ".next/",
    ".cache/",
    "coverage/",
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

SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".mp4", ".mp3",
    ".wav", ".pkl", ".pickle", ".pt", ".pth", ".onnx", ".h5", ".wasm", ".bin",
    ".pdf", ".engine", ".weights",
}


def should_index_file(repo_path: Path, file: Path) -> bool:
    relative = rel(repo_path, file)
    lower = relative.lower()
    ext = file.suffix.lower()

    if ext in SKIP_EXTS:
        return False

    if ext not in INDEXABLE_EXTS:
        return False

    if any(hint in lower for hint in SKIP_PATH_HINTS):
        return False

    try:
        if file.stat().st_size > 180_000:
            return False
    except OSError:
        return False

    if lower.startswith("assets/") and ext not in {".md", ".rst", ".txt"}:
        return False

    return True


def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]{1,}|[0-9]+", text.lower())


def embed_text(text: str) -> List[float]:
    vec = [0.0] * VECTOR_DIM
    tokens = tokenize(text)

    if not tokens:
        return vec

    for token in tokens:
        h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
        idx = h % VECTOR_DIM
        sign = 1.0 if ((h >> 8) & 1) else -1.0
        vec[idx] += sign

    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def normalize_cosine_score(score: float) -> float:
    return max(0.0, min(1.0, (score + 1.0) / 2.0))


def distance_to_similarity(distance: float) -> float:
    # Chroma returns a distance. Smaller is better. This maps it into a readable 0-1 score.
    return 1.0 / (1.0 + max(0.0, float(distance)))


def chunk_text(text: str, max_lines: int = 80, overlap: int = 12) -> List[Tuple[int, int, str]]:
    lines = text.splitlines()
    chunks = []

    if not lines:
        return chunks

    start = 0

    while start < len(lines):
        end = min(len(lines), start + max_lines)
        chunk = "\n".join(lines[start:end]).strip()

        if chunk:
            chunks.append((start + 1, end, chunk))

        if end >= len(lines):
            break

        start = max(0, end - overlap)

    return chunks


def collect_chunks(repo_path: Path, max_chunks: int = 1200) -> List[Dict[str, Any]]:
    chunks = []

    for file in iter_files(repo_path):
        if not should_index_file(repo_path, file):
            continue

        text = safe_read(file, 120_000)

        if not text.strip():
            continue

        for start, end, chunk in chunk_text(text):
            chunks.append(
                {
                    "file_path": rel(repo_path, file),
                    "start_line": start,
                    "end_line": end,
                    "text": chunk,
                }
            )

            if len(chunks) >= max_chunks:
                return chunks

    return chunks


class LocalVectorStore:
    def __init__(self):
        self.backend_name = "local-json-vector-store"

    def _path(self, repo_id: str) -> Path:
        return VECTOR_DIR / f"{repo_id}.vectors.json"

    def build(self, repo_id: str, repo_path: Path) -> Dict[str, Any]:
        chunks = collect_chunks(repo_path)
        records = []

        for i, chunk in enumerate(chunks):
            records.append(
                {
                    "id": f"{repo_id}-{i}",
                    "embedding": embed_text(chunk["text"]),
                    **chunk,
                }
            )

        self._path(repo_id).write_text(json.dumps(records), encoding="utf-8")

        return {
            "backend": self.backend_name,
            "chunks_indexed": len(records),
        }

    def query(self, repo_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        path = self._path(repo_id)

        if not path.exists():
            return []

        records = json.loads(path.read_text(encoding="utf-8"))
        q = embed_text(query)

        scored = []

        for record in records:
            raw_cosine = cosine(q, record["embedding"])
            similarity = normalize_cosine_score(raw_cosine)
            scored.append((similarity, record))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []

        for similarity, record in scored[:top_k]:
            results.append(
                {
                    "score": round(float(similarity), 4),
                    "file_path": record["file_path"],
                    "start_line": record["start_line"],
                    "end_line": record["end_line"],
                    "text": record["text"][:1600],
                }
            )

        return results


class ChromaVectorStore:
    def __init__(self):
        import chromadb

        self.client = chromadb.PersistentClient(path=str(VECTOR_DIR / "chroma"))
        self.backend_name = "chromadb-hashed-embeddings"

    def _collection(self, repo_id: str):
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", repo_id)[:60]
        return self.client.get_or_create_collection(name=f"repo_{safe}")

    def build(self, repo_id: str, repo_path: Path) -> Dict[str, Any]:
        collection = self._collection(repo_id)

        try:
            existing = collection.get()
            ids = existing.get("ids", [])

            if ids:
                collection.delete(ids=ids)
        except Exception:
            pass

        chunks = collect_chunks(repo_path)

        if not chunks:
            return {
                "backend": self.backend_name,
                "chunks_indexed": 0,
            }

        ids = []
        docs = []
        metas = []
        embeddings = []

        for i, chunk in enumerate(chunks):
            ids.append(f"{repo_id}-{i}")
            docs.append(chunk["text"])
            metas.append(
                {
                    "file_path": chunk["file_path"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                }
            )
            embeddings.append(embed_text(chunk["text"]))

        batch = 200

        for start in range(0, len(ids), batch):
            collection.add(
                ids=ids[start : start + batch],
                documents=docs[start : start + batch],
                metadatas=metas[start : start + batch],
                embeddings=embeddings[start : start + batch],
            )

        return {
            "backend": self.backend_name,
            "chunks_indexed": len(ids),
        }

    def query(self, repo_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        collection = self._collection(repo_id)

        result = collection.query(
            query_embeddings=[embed_text(query)],
            n_results=top_k,
        )

        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        out = []

        for doc, meta, dist in zip(docs, metas, distances):
            similarity = distance_to_similarity(dist)

            out.append(
                {
                    "score": round(similarity, 4),
                    "file_path": meta.get("file_path", "unknown"),
                    "start_line": meta.get("start_line", 1),
                    "end_line": meta.get("end_line", 1),
                    "text": doc[:1600],
                }
            )

        return out


def get_vector_store():
    try:
        return ChromaVectorStore()
    except Exception:
        return LocalVectorStore()
