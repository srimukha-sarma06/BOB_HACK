import os
from typing import Dict, Any

from dotenv import load_dotenv

load_dotenv()


def fallback_summary(analysis: Dict[str, Any], tree_preview: str = "") -> str:
    good_files = analysis.get("good_first_files", [])[:4]
    risky_files = analysis.get("risky_files", [])[:4]
    file_groups = analysis.get("file_groups", {})

    lines = [
        f"# Architecture Summary for {analysis.get('repo_name', 'repository')}",
        "",
        "## Repository overview",
        f"- Total files analyzed: {analysis.get('total_files')}",
        f"- Main languages: {', '.join(analysis.get('languages', {}).keys())}",
        f"- Package/build system: {analysis.get('package_manager')}",
        f"- Entry points: {', '.join(analysis.get('entrypoints', [])) or 'No obvious entrypoint detected'}",
        f"- Tests: {', '.join(analysis.get('test_files', [])) or 'No tests detected'}",
        "",
        "## Important areas detected",
    ]

    for group_name, items in file_groups.items():
        if items:
            lines.append(f"- {group_name}: {', '.join(items[:5])}")

    lines += [
        "",
        "## Good first contribution candidates",
    ]

    if good_files:
        for item in good_files:
            lines.append(f"- `{item['file']}`: {item['reason']} (score {item['score']})")
    else:
        lines.append("- No obvious good-first files detected by static analysis.")

    lines += [
        "",
        "## Risky areas to avoid first",
    ]

    if risky_files:
        for item in risky_files:
            lines.append(f"- `{item['file']}`: {item['reason']} (score {item['score']})")
    else:
        lines.append("- No major risky files detected by static analysis.")

    lines += [
        "",
        "## Suggested Bob workflow",
        "Use the Bob Missions tab to ask IBM Bob to explain the repo, choose a safe task, create an implementation plan, add tests, and produce a PR summary.",
    ]

    return "\n".join(lines)


def generate_architecture_summary(analysis: Dict[str, Any], tree_preview: str = "") -> str:
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not groq_key and not openai_key:
        return fallback_summary(analysis, tree_preview)

    try:
        from openai import OpenAI

        if groq_key:
            client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        else:
            client = OpenAI(api_key=openai_key)
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        prompt = f"""
You are a senior software engineer helping a beginner onboard to a repository.

Analyze this static scan and file tree preview.

Static analysis:
{analysis}

File tree preview:
{tree_preview}

Return a concise markdown architecture summary with:
1. What the repo appears to do
2. Main components
3. How to run/test if inferable
4. Good first contribution candidates
5. Risky areas to avoid
6. How IBM Bob should be used next
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You explain repositories clearly for beginner contributors."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=900,
        )

        return response.choices[0].message.content

    except Exception as exc:
        return fallback_summary(analysis, tree_preview) + f"\n\nLLM summary failed, so local static summary was used: `{exc}`"
