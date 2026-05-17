First PR Mentor - Mission Recommendations for broken-task-api
🎯 Mission 1: Add Email Validation to User Creation
Title: Implement email validation in user registration

User Impact: Prevents invalid email addresses from being stored in the system, improving data quality and reducing potential bugs downstream.

Files Affected:

src/routes/users.py (add validation logic)
tests/test_users.py (add test cases)
Why It's Safe:

Explicit TODO comment in the code (# TODO: reject invalid email values)
Small, isolated feature-level file (11 lines)
Doesn't touch database or authentication logic
Test file exists nearby for validation
Clear scope with minimal side effects
Expected Code Change:

import re

def create_user(payload):
    username = payload.get("username")
    email = payload.get("email")
    
    # Validate email format
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Invalid email address")
    
    # Validate username
    if not username:
        raise ValueError("Username is required")
    
    user = {"username": username, "email": email}
    return save_user(user)

Test Strategy:

Add test for valid email (passes)
Add test for invalid email format (raises ValueError)
Add test for missing email (raises ValueError)
Add test for empty username (raises ValueError)
All tests should use pytest.raises for error cases
Risk Level: 🟢 LOW

No database schema changes
No authentication changes
Clear requirements from TODO
Easy to test and verify
🎯 Mission 2: Expand README Setup Instructions
Title: Complete README setup documentation

User Impact: New contributors and users can set up the project faster with clear, complete instructions.

Files Affected:

README.md (add setup steps, usage examples, project structure)
Why It's Safe:

Documentation-only change
Explicitly mentioned in README gaps: "README setup is incomplete"
No code execution risk
Easy to review and iterate
Can't break functionality
Expected Code Change:

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd broken-task-api

Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Usage
Run tests:

pytest

Project Structure
broken-task-api/
├── app.py              # Main application entry
├── src/
│   ├── routes/         # API route handlers
│   │   ├── users.py    # User management
│   │   ├── tasks.py    # Task management
│   │   └── health.py   # Health check
│   ├── db.py           # Database operations
│   └── auth.py         # Authentication
└── tests/              # Test suite


**Test Strategy:**
- Manual review of documentation clarity
- Follow instructions on fresh environment
- Verify all commands work as documented
- Check for typos and formatting

**Risk Level:** 🟢 VERY LOW
- Zero code changes
- Cannot break functionality
- Easy to revert if needed

---

## 🎯 Mission 3: Add Negative Test Cases for User Creation
**Title:** Add test coverage for invalid user payloads

**User Impact:** Improves code reliability by ensuring the system properly handles bad input, preventing future bugs.

**Files Affected:**
- `tests/test_users.py` (add new test functions)

**Why It's Safe:**
- Test-only changes
- Explicitly mentioned in README gaps: "tests do not cover bad user payloads"
- Nearby test file already exists (6 lines, easy to understand)
- No production code changes
- Tests document expected behavior

**Expected Code Change:**
```python
import pytest
from src.routes.users import create_user


def test_create_user():
    user = create_user({"username": "mayuur", "email": "mayuur@example.com"})
    assert user["username"] == "mayuur"


def test_create_user_rejects_invalid_email():
    with pytest.raises(ValueError):
        create_user({"username": "mayuur", "email": "not-an-email"})


def test_create_user_rejects_missing_email():
    with pytest.raises(ValueError):
        create_user({"username": "mayuur"})


def test_create_user_rejects_empty_username():
    with pytest.raises(ValueError):
        create_user({"username": "", "email": "mayuur@example.com"})


def test_create_user_rejects_missing_username():
    with pytest.raises(ValueError):
        create_user({"email": "mayuur@example.com"})


Test Strategy:

Run pytest to verify tests fail initially (since validation isn't implemented)
Tests serve as specification for Mission 1
Can be merged independently to document expected behavior
All tests should use pytest.raises pattern
Risk Level: 🟢 VERY LOW

Test-only changes
No production code modified
Easy to verify correctness
Can be merged before implementation
🏆 RECOMMENDED BEST FIRST MISSION: Mission 2 (README Documentation)
Why This Is The Best Choice:

Zero Risk: Documentation changes cannot break code or tests
Immediate Value: Helps all future contributors and users
Quick Win: Can be completed in 15-30 minutes
No Dependencies: Doesn't require understanding complex code logic
Easy Review: Maintainers can quickly approve documentation PRs
Builds Confidence: Success on first PR encourages continued contribution
Explicitly Requested: README gaps are listed in the project's own documentation
No Setup Required: Can be done entirely in GitHub's web editor
Universal Skill: Writing documentation is valuable across all projects
Gateway Mission: Understanding project structure through documentation helps with future code contributions
Progression Path:

Start with Mission 2 (README) → builds project understanding
Then Mission 3 (Tests) → learns testing patterns
Finally Mission 1 (Validation) → implements actual feature with tests
This progression takes a contributor from documentation → testing → implementation, building skills incrementally while delivering value at each step.
