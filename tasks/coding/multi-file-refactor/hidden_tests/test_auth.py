#!/usr/bin/env python3
"""Hidden oracle: verifies auth feature is correctly implemented across all 3 files."""
import subprocess, sys

TESTS = r'''
import sys, json
sys.path.insert(0, ".")

errors = []

# 1. config.py must have auth_tokens
try:
    from config import auth_tokens
    if not isinstance(auth_tokens, dict):
        errors.append(f"config.auth_tokens should be dict, got {type(auth_tokens)}")
    elif len(auth_tokens) == 0:
        errors.append("config.auth_tokens is empty")
except ImportError:
    errors.append("config.auth_tokens not found")

# 2. models.py must have authenticate function
try:
    from models import authenticate
    # Valid token should return a username string
    from config import auth_tokens
    test_token = list(auth_tokens.keys())[0]
    result = authenticate(test_token)
    if result != auth_tokens[test_token]:
        errors.append(f"authenticate(valid_token) returned {result!r}, expected {auth_tokens[test_token]!r}")
    # Invalid token should return None
    if authenticate("nonexistent-token-xyz") is not None:
        errors.append("authenticate(invalid_token) should return None")
except ImportError:
    errors.append("models.authenticate not found")

# 3. server.py handle_request must enforce auth on protected paths
try:
    from server import handle_request
    from config import auth_tokens
    valid_token = list(auth_tokens.keys())[0]

    # No Authorization header -> should still work (public)
    status, _, _ = handle_request("GET", "/users", {})
    if status != 200:
        errors.append(f"GET /users without auth returned {status}, expected 200 (public)")

    # Invalid token -> 401
    status, _, body = handle_request("GET", "/users", {"Authorization": "Bearer bad-token"})
    if status != 401:
        errors.append(f"GET /users with bad token returned {status}, expected 401")

    # Valid token -> 200
    status, _, _ = handle_request("GET", "/users", {"Authorization": f"Bearer {valid_token}"})
    if status != 200:
        errors.append(f"GET /users with valid token returned {status}, expected 200")

    # Missing "Bearer " prefix -> 401
    status, _, _ = handle_request("GET", "/users", {"Authorization": valid_token})
    if status != 401:
        errors.append(f"GET /users with token but no Bearer prefix returned {status}, expected 401")

except ImportError as e:
    errors.append(f"server import failed: {e}")

# 4. Existing functionality must still work
try:
    from server import handle_request
    status, _, body = handle_request("GET", "/users/alice", {})
    if status != 200 or "alice" not in body:
        errors.append(f"regression: GET /users/alice returned {status}")

    status, _, body = handle_request("POST", "/echo", {}, "test")
    if status != 200 or body != "test":
        errors.append(f"regression: POST /echo returned {status}")
except Exception as e:
    errors.append(f"regression check failed: {e}")

TOTAL = 10
passed = TOTAL - len(errors)
print(f"SCORE: {passed}/{TOTAL}")
if errors:
    print("FAIL:")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (auth feature correct, no regressions)")
'''

r = subprocess.run([sys.executable, "-c", TESTS], capture_output=True, text=True, timeout=20)
print(r.stdout.strip())
if r.stderr.strip(): print(r.stderr.strip(), file=sys.stderr)
sys.exit(r.returncode)
