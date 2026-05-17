from typing import Dict, Any


def bullet_files(items):
    if not items:
        return "- None found"
    lines = []
    for item in items:
        if isinstance(item, dict):
            lines.append(f"- {item.get('file')}: {item.get('reason', '')}")
        else:
            lines.append(f"- {item}")
    return "\\n".join(lines)


def generate_bob_prompts(analysis: Dict[str, Any]) -> Dict[str, str]:
    repo_name = analysis.get("repo_name", "the repository")
    good = bullet_files(analysis.get("good_first_files", []))
    risky = bullet_files(analysis.get("risky_files", []))
    entrypoints = ", ".join(analysis.get("entrypoints", [])) or "unknown"
    tests = ", ".join(analysis.get("test_files", [])) or "none found"

    understand = f"""You are First PR Mentor, a senior maintainer helping a beginner understand an unfamiliar repository.

Repository: {repo_name}

Static analysis hints:
- Onboarding score: {analysis.get('onboarding_score')}/100
- Entry points: {entrypoints}
- Test files: {tests}
- Package manager: {analysis.get('package_manager', 'unknown')}
- TODO/FIXME count: {analysis.get('todo_count', 'unknown')}

Beginner-friendly files:
{good}

Risky files to avoid first:
{risky}

Return exactly these sections:
1. Repository in one paragraph
2. Architecture map for a beginner
3. Important files and why they matter
4. How to run locally
5. How tests seem to work
6. Files a beginner should avoid touching first
7. Best areas for a safe first contribution
"""

    tasks = f"""You are First PR Mentor.

Based on the full repository and static scan below, suggest safe first contribution tasks.

Repository: {repo_name}
Good first candidates:
{good}

Risky files to avoid:
{risky}

Generate 3 first-PR missions. For each mission include:
- Title
- User impact
- Files affected
- Why it is safe
- Expected code change
- Test strategy
- Risk level

Then choose the single best mission and explain why.
"""

    implement = """You are First PR Mentor. Implement the selected first-PR mission.

Rules:
1. Make the smallest correct code change.
2. Avoid broad refactors.
3. Add or update tests.
4. Run the available test command if possible.
5. If tests fail, diagnose and fix once.
6. Produce a clean PR summary.

Output sections:
1. Implementation plan
2. Files changed
3. Tests added or updated
4. Commands run
5. Known limitations
6. Pull request title
7. Pull request summary
8. Reviewer notes
"""

    review = """You are First PR Mentor. Review the final diff for a beginner's first contribution.

Check:
1. Is the change small and safe?
2. Are tests included?
3. Are risky files avoided?
4. Is the PR summary clear?
5. What should the beginner explain in an interview?

Return:
- Approval status
- Concerns
- Suggested fixes
- Final PR explanation
"""

    return {
        "understand": understand,
        "tasks": tasks,
        "implement": implement,
        "review": review,
    }
