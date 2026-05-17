import React, { useMemo, useState } from "react";

const API = "http://127.0.0.1:8000";

const emptyArtifacts = {
  "bob-architecture-summary": "",
  "bob-task-selection": "",
  "bob-implementation-plan": "",
  "bob-pr-summary": "",
};

function Icon({ name }) {
  const map = {
    wand: "✦",
    repo: "☾",
    map: "🗺",
    shield: "🛡",
    test: "⚗",
    pr: "⑂",
    search: "⌕",
    scroll: "卷",
    star: "★",
    book: "📜",
  };
  return <span className="icon">{map[name] || "✦"}</span>;
}

function scoreClass(score) {
  if (score >= 75) return "good";
  if (score >= 45) return "mid";
  return "bad";
}

function Header() {
  return (
    <header className="header">
      <div className="brand-mark"><Icon name="wand" /></div>
      <div>
        <div className="eyebrow">Bob-powered developer onboarding</div>
        <h1>FirstPR <span>Academy</span></h1>
      </div>
      <div className="header-pill">Unknown repo → safe mission → tested PR</div>
    </header>
  );
}

function RepoInput({ repoUrl, setRepoUrl, analyze, analyzeSample, loading }) {
  return (
    <section className="hero card">
      <div className="hero-copy">
        <div className="mini-pill"><Icon name="book" /> Enchanted repo onboarding</div>
        <h2>Turn a strange codebase into your first useful pull request.</h2>
        <p>
          Paste a GitHub repo. FirstPR scans it, builds a vector index, finds safe beginner paths,
          generates Bob missions, and stores final PR artifacts.
        </p>
        <div className="input-row">
          <input
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/user/repo"
          />
          <button onClick={analyze} disabled={loading}>{loading ? "Casting..." : "Analyze Repo"}</button>
        </div>
        <button className="link-button" onClick={analyzeSample} disabled={loading}>
          Use sample repo instead
        </button>
      </div>

      <div className="ritual parchment">
        <h3><Icon name="scroll" /> The FirstPR ritual</h3>
        {[
          ["Summon", "Clone and scan repository structure"],
          ["Reveal", "Show entrypoints, tests, docs, and risky zones"],
          ["Index", "Build a vector index for semantic code search"],
          ["Ask Bob", "Generate repo-aware Bob missions"],
          ["Submit", "Collect PR summary and Bob artifacts"],
        ].map(([title, text], i) => (
          <div className="ritual-step" key={title}>
            <b>{i + 1}</b>
            <div><strong>{title}</strong><span>{text}</span></div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Overview({ analysis }) {
  const langs = Object.entries(analysis.languages || {}).map(([k, v]) => `${k}: ${v}`).join(" · ");
  return (
    <div className="overview-grid">
      <section className="card score-card">
        <div>
          <div className="eyebrow">Onboarding charm</div>
          <h2>{analysis.repo_name}</h2>
          <a href={analysis.repo_url} target="_blank" rel="noreferrer">{analysis.repo_url}</a>
        </div>
        <div className={`score-orb ${scoreClass(analysis.onboarding_score)}`}>
          <span>{analysis.onboarding_score}</span>
          <small>/100</small>
        </div>
        <div className="time-box">
          <p>Manual onboarding: <b>{analysis.estimated_manual_minutes} min</b></p>
          <p>With FirstPR: <b>{analysis.estimated_firstpr_minutes} min</b></p>
        </div>
      </section>

      <section className="stat-grid">
        <Stat label="Languages" value={Object.keys(analysis.languages || {}).length} sub={langs} icon="repo" />
        <Stat label="Tests found" value={(analysis.test_files || []).length} sub={(analysis.test_files || []).slice(0, 2).join(", ") || "None"} icon="test" />
        <Stat label="Docs" value={analysis.readme_exists ? "README" : "Missing"} sub={(analysis.docs || []).slice(0, 2).join(", ") || "No docs"} icon="scroll" />
        <Stat label="Vector index" value={analysis.vector_index_ready ? "Ready" : "Missing"} sub={`${analysis.vector_index?.backend || "unknown"} · ${analysis.vector_index?.chunks_indexed || 0} chunks`} icon="search" />
      </section>

      <section className="card wide">
        <h3>Architecture Summary</h3>
        <pre className="markdown-box">{analysis.architecture_summary}</pre>
      </section>
    </div>
  );
}

function Stat({ label, value, sub, icon }) {
  return (
    <div className="card stat">
      <div><span>{label}</span><b>{value}</b><small>{sub}</small></div>
      <Icon name={icon} />
    </div>
  );
}

function FileMap({ analysis }) {
  const groups = analysis.file_groups || {};
  return (
    <div className="two-col">
      <section className="card">
        <h2><Icon name="map" /> Repo Map</h2>
        <div className="group-grid">
          {Object.entries(groups).map(([name, files]) => (
            <div className="parchment group" key={name}>
              <h4>{name}</h4>
              {(files || []).length ? files.map((f) => <FileBadge key={f} file={f} />) : <p className="muted">None detected</p>}
            </div>
          ))}
        </div>
      </section>

      <section className="stack">
        <div className="card">
          <h3><Icon name="star" /> Good First Files</h3>
          {(analysis.good_first_files || []).map((f) => (
            <FileBadge key={f.file} file={`${f.file} · ${f.score}`} sub={f.reason} tone="good" />
          ))}
        </div>
        <div className="card">
          <h3><Icon name="shield" /> Forbidden Forest Files</h3>
          {(analysis.risky_files || []).map((f) => (
            <FileBadge key={f.file} file={f.file} sub={f.reason} tone="risk" />
          ))}
        </div>
      </section>
    </div>
  );
}

function FileBadge({ file, sub, tone = "" }) {
  return (
    <div className={`file-badge ${tone}`}>
      <strong>{file}</strong>
      {sub && <span>{sub}</span>}
    </div>
  );
}

function VectorSearch({ analysis }) {
  const [query, setQuery] = useState("where should I add email validation?");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  async function search() {
    setLoading(true);
    try {
      const res = await fetch(`${API}/repos/${analysis.repo_id}/semantic-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 6 }),
      });
      const data = await res.json();
      setResults(data.results || []);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2><Icon name="search" /> Vector Search Chamber</h2>
      <p className="muted">
        This is real backend semantic search over indexed repo chunks. It uses ChromaDB if available,
        otherwise the built-in vector store fallback.
      </p>
      <div className="input-row">
        <input value={query} onChange={(e) => setQuery(e.target.value)} />
        <button onClick={search} disabled={loading}>{loading ? "Searching..." : "Search Meaning"}</button>
      </div>

      <div className="result-grid">
        {results.map((r, i) => (
          <div className="parchment result" key={`${r.file_path}-${i}`}>
            <div className="result-head">
              <b>#{i + 1}</b>
              <span>score {r.score}</span>
            </div>
            <h4>{r.file_path}</h4>
            <small>lines {r.start_line}-{r.end_line}</small>
            <pre>{r.text}</pre>
          </div>
        ))}
      </div>
    </section>
  );
}

function BobMissions({ analysis }) {
  const prompts = analysis.bob_prompts || {};
  const cards = [
    ["understand", "Spell 1: Understand the repo"],
    ["tasks", "Spell 2: Select first PR mission"],
    ["implement", "Spell 3: Implement + test"],
    ["review", "Spell 4: Review final diff"],
  ];

  return (
    <div className="prompt-grid">
      {cards.map(([key, title]) => (
        <section className="card prompt-card" key={key}>
          <div className="prompt-head">
            <h3><Icon name="wand" /> {title}</h3>
            <CopyButton text={prompts[key] || ""} />
          </div>
          <pre>{prompts[key] || "Prompt missing"}</pre>
        </section>
      ))}
    </div>
  );
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try { await navigator.clipboard.writeText(text); } catch {}
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  }
  return <button className="small-btn" onClick={copy}>{copied ? "Copied" : "Copy"}</button>;
}

function Artifacts({ analysis }) {
  const [artifacts, setArtifacts] = useState(emptyArtifacts);
  const [saved, setSaved] = useState("");

  async function saveOne(key) {
    await fetch(`${API}/repos/${analysis.repo_id}/artifacts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ artifact_type: key, content: artifacts[key] }),
    });
    setSaved(key);
    setTimeout(() => setSaved(""), 1200);
  }

  return (
    <div className="two-col">
      <section className="card">
        <h2><Icon name="scroll" /> Bob Artifact Vault</h2>
        {Object.keys(artifacts).map((key) => (
          <div className="artifact-input" key={key}>
            <label>{key}</label>
            <textarea value={artifacts[key]} onChange={(e) => setArtifacts({ ...artifacts, [key]: e.target.value })} />
            <button className="small-btn" onClick={() => saveOne(key)}>{saved === key ? "Saved" : "Save"}</button>
          </div>
        ))}
      </section>

      <section className="card">
        <h2><Icon name="pr" /> Final Submission Dashboard</h2>
        {Object.entries(artifacts).map(([key, value]) => (
          <div className="parchment artifact-preview" key={key}>
            <h4>{key}</h4>
            <pre>{value || "Waiting for Bob output..."}</pre>
          </div>
        ))}
      </section>
    </div>
  );
}

function Checklist({ analysis }) {
  const items = [
    ["Repo analyzed", !!analysis],
    ["Vector index built", !!analysis?.vector_index_ready],
    ["Bob prompts generated", !!analysis?.bob_prompts],
    ["Architecture summary generated", !!analysis?.architecture_summary],
    ["Good First PR files scored", (analysis?.good_first_files || []).length > 0],
    ["Risky files identified", (analysis?.risky_files || []).length > 0],
    ["Official IBM Bob report exported manually", false],
  ];

  return (
    <section className="card">
      <h2><Icon name="star" /> Submission Checklist</h2>
      <div className="checklist">
        {items.map(([label, ok]) => (
          <div className={`check ${ok ? "yes" : "no"}`} key={label}>
            <b>{ok ? "✓" : "!"}</b>
            <span>{label}</span>
          </div>
        ))}
      </div>
      <p className="muted">
        The last item must be done from your IBM Bob account during the hackathon. Everything else is included here.
      </p>
    </section>
  );
}

export default function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [tab, setTab] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    if (!repoUrl.trim()) {
      setError("Paste a GitHub repo URL or use the sample repo.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const name = repoUrl.trim().split("/").filter(Boolean).pop()?.replace(".git", "") || "repo";
      const res = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_link: repoUrl.trim(), repo_name: name, repo_description: "Analyzed by FirstPR Academy" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analyze failed");
      setAnalysis(data);
      setTab("overview");
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  async function analyzeSample() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/analyze-sample`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Sample analyze failed");
      setRepoUrl(data.repo_url);
      setAnalysis(data);
      setTab("overview");
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  const tabs = useMemo(() => [
    ["overview", "Overview"],
    ["map", "Repo Map"],
    ["vector", "Vector Search"],
    ["bob", "Bob Missions"],
    ["artifacts", "Artifacts"],
    ["checklist", "Submit"],
  ], []);

  return (
    <main className="app">
      <div className="bg-sparks" />
      <Header />
      <RepoInput repoUrl={repoUrl} setRepoUrl={setRepoUrl} analyze={analyze} analyzeSample={analyzeSample} loading={loading} />
      {error && <div className="error">{error}</div>}

      {analysis && (
        <>
          <nav className="tabs">
            {tabs.map(([id, label]) => (
              <button key={id} className={tab === id ? "active" : ""} onClick={() => setTab(id)}>{label}</button>
            ))}
          </nav>

          {tab === "overview" && <Overview analysis={analysis} />}
          {tab === "map" && <FileMap analysis={analysis} />}
          {tab === "vector" && <VectorSearch analysis={analysis} />}
          {tab === "bob" && <BobMissions analysis={analysis} />}
          {tab === "artifacts" && <Artifacts analysis={analysis} />}
          {tab === "checklist" && <Checklist analysis={analysis} />}
        </>
      )}

      <footer>FirstPR Academy · Bob-powered first contribution workflow · Full-stack + vector search + artifact vault</footer>
    </main>
  );
}
