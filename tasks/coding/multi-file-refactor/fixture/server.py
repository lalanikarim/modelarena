"""A minimal HTTP request handler (no framework, stdlib only)."""
import json
import sys

from config import HOST, PORT, MAX_BODY_SIZE
from models import get_user, list_users


def handle_request(method: str, path: str, headers: dict, body: str = "") -> tuple[int, dict, str]:
    """Return (status_code, headers, body) for a request."""
    # Routing
    if method == "GET" and path == "/users":
        users = [{"username": u.username, "email": u.email} for u in list_users()]
        return 200, {"Content-Type": "application/json"}, json.dumps(users)

    if method == "GET" and path.startswith("/users/"):
        username = path[len("/users/"):]
        user = get_user(username)
        if user is None:
            return 404, {"Content-Type": "application/json"}, json.dumps({"error": "not found"})
        return 200, {"Content-Type": "application/json"}, json.dumps(
            {"username": user.username, "email": user.email}
        )

    if method == "POST" and path == "/echo":
        return 200, {"Content-Type": "application/json"}, body

    return 404, {"Content-Type": "application/json"}, json.dumps({"error": "not found"})


def self_test() -> bool:
    """Run a few assertions to verify the handler works."""
    ok = True

    status, _, body = handle_request("GET", "/users", {})
    if status != 200:
        print(f"FAIL: GET /users returned {status}"); ok = False

    status, _, body = handle_request("GET", "/users/alice", {})
    if status != 200 or "alice" not in body:
        print(f"FAIL: GET /users/alice returned {status} {body[:80]}"); ok = False

    status, _, _ = handle_request("GET", "/users/nobody", {})
    if status != 404:
        print(f"FAIL: GET /users/nobody returned {status}, expected 404"); ok = False

    status, _, body = handle_request("POST", "/echo", {}, "hello")
    if status != 200 or body != "hello":
        print(f"FAIL: POST /echo returned {status} {body[:80]}"); ok = False

    if ok:
        print("self-test: all checks passed")
    return ok


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    print(f"Server would listen on {HOST}:{PORT} (no actual socket in this fixture)")
