First PR Mentor Guide: broken-task-api
1. Repository in one paragraph
The broken-task-api is a minimal FastAPI-style Python project designed as a learning sandbox for first-time contributors. It provides a simple REST API for managing users and tasks with intentional gaps (missing email validation, incomplete README, missing test coverage) that serve as beginner-friendly contribution opportunities. The codebase uses an in-memory database simulation, basic route handlers, and pytest for testing, making it an ideal starting point for understanding web API fundamentals without the complexity of real database connections or authentication systems.

2. Architecture map for a beginner
broken-task-api/
├── app.py                    # Main entry point - imports and exposes core functions
├── requirements.txt          # Python dependencies (fastapi, pytest, pydantic)
├── src/                      # Source code directory
│   ├── routes/              # API endpoint handlers (the "controllers")
│   │   ├── users.py         # User creation logic (has TODOs!)
│   │   ├── tasks.py         # Task creation logic (validation example)
│   │   └── health.py        # Simple health check endpoint
│   ├── db.py                # Fake database (just Python lists)
│   └── auth.py              # Token verification (keep away for now)
└── tests/                   # Test suite
    ├── test_users.py        # Tests for user creation
    └── test_tasks.py        # Tests for task creation (includes error case)

Data flow: Request → Route handler (users.py/tasks.py) → Database layer (db.py) → Response

3. Important files and why they matter
app.py: The application's main entry point that imports and wires together all route functions. Think of it as the "table of contents" for the API.

src/routes/users.py: Handles user creation with clear TODOs for validation. This is where you'd add email format checking and username validation - perfect for learning input validation patterns.

src/routes/tasks.py: Shows a complete example of input validation (checking for empty title). Use this as a reference when fixing users.py.

src/db.py: Simulates a database using Python lists. While marked "risky," it's actually simple - just avoid changing it until you understand how routes depend on it.

tests/test_users.py & tests/test_tasks.py: Show how to write tests. Notice test_tasks.py has both success and error cases, while test_users.py only tests the happy path (opportunity for contribution!).

README.md: Documents known gaps and has incomplete setup instructions - safe documentation improvements are always welcome.

4. How to run locally
# Install dependencies
pip install -r requirements.txt

# Run tests (this is the main way to verify the code works)
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_users.py

Note: This project doesn't have a web server setup yet - it's designed for testing the business logic directly. The functions can be imported and called from Python, and tests verify they work correctly.

5. How tests seem to work
The test suite uses pytest, Python's popular testing framework:

Test files: Located in tests/ directory, named test_*.py
Test functions: Start with test_ prefix (e.g., test_create_user)
Assertions: Use assert statements to verify expected behavior
Error testing: Uses pytest.raises() context manager to verify exceptions (see test_create_task_rejects_empty_title)
Current coverage:

✅ Tasks: Tests both success case and error handling
⚠️ Users: Only tests success case - missing validation tests for bad emails/empty usernames
To run: Simply execute pytest in the project root. Green dots = passing tests.

6. Files a beginner should avoid touching first
src/auth.py: Authentication/security logic is sensitive. Even though this is a simple demo, it's marked as risky because auth bugs can have security implications. Learn the codebase first.

src/db.py: The database layer is a dependency for all routes. Changing it could break multiple features at once. While simple, it's a "shared infrastructure" file - better to start with isolated route handlers.

Why avoid these? They're foundational pieces that other code depends on. Start with "leaf" files (routes, tests, docs) that don't have many dependents.

7. Best areas for a safe first contribution
🌟 Highest confidence starter tasks:

Fix TODO in src/routes/users.py (lines 5-6):

Add email validation (check for @ symbol, basic format)
Add username validation (reject empty/None values)
Reference tasks.py (line 6-7) for validation pattern
Add corresponding tests in test_users.py
Improve test coverage in tests/test_users.py:

Add test for invalid email (e.g., "notanemail")
Add test for empty username
Follow the pattern from test_tasks.py lines 10-12
Complete README.md documentation:

Add more detailed setup instructions
Document what each route does
Add examples of how to use the functions
Explain the project structure
Why these are safe:

They're isolated changes that don't affect core infrastructure
Clear TODOs guide what needs to be done
Existing code provides patterns to follow
Tests will catch if you break something
Documentation changes can't break the code
Recommended first PR: Pick the TODO in users.py - it's small, has clear requirements, existing validation patterns to copy from tasks.py, and you can immediately add tests to verify your fix works.
