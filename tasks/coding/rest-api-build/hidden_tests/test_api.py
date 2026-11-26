#!/usr/bin/env python3
"""Hidden oracle: starts the API server and tests all endpoints."""
import subprocess, sys, json, time, signal, os
import urllib.request
import urllib.error

def wait_for_server(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/items", timeout=2)
            return True
        except Exception:
            time.sleep(0.3)
    return False

def req(method, url, body=None):
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, method=method)
    if data:
        r.headers["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

errors = []
PORT = 9701  # Use different port to avoid conflicts

# Start server on our port (override via env or arg)
proc = subprocess.Popen(
    [sys.executable, "api.py", "--port", str(PORT)],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd=".",
)

try:
    if not wait_for_server(PORT):
        print("FAIL: server did not start")
        sys.exit(1)

    # 1. POST /items — create valid items
    status, body = req("POST", f"http://127.0.0.1:{PORT}/items",
                      {"name": "Widget", "category": "tools", "price": 9.99})
    if status != 201:
        errors.append(f"POST valid: got {status}, expected 201")
    elif "id" not in body or body["id"] != 1:
        errors.append(f"POST valid: expected id=1, got {body}")

    status, body = req("POST", f"http://127.0.0.1:{PORT}/items",
                      {"name": "Gadget", "category": "Tools", "price": 24.5})
    if status != 201 or body.get("id") != 2:
        errors.append(f"POST second: got {status} {body}")

    # 2. POST validation failures
    status, _ = req("POST", f"http://127.0.0.1:{PORT}/items",
                   {"name": "", "category": "x", "price": 1})
    if status != 400:
        errors.append(f"POST empty name: got {status}, expected 400")

    status, _ = req("POST", f"http://127.0.0.1:{PORT}/items",
                   {"name": "X", "category": "y", "price": -5})
    if status != 400:
        errors.append(f"POST negative price: got {status}, expected 400")

    status, _ = req("POST", f"http://127.0.0.1:{PORT}/items",
                   {"name": "X"})  # missing category and price
    if status != 400:
        errors.append(f"POST missing fields: got {status}, expected 400")

    # 3. GET /items — all
    status, body = req("GET", f"http://127.0.0.1:{PORT}/items")
    if status != 200 or not isinstance(body, list) or len(body) != 2:
        errors.append(f"GET all: got {status} len={len(body) if isinstance(body, list) else '?'}")

    # 4. GET /items?category=tools (case-insensitive)
    status, body = req("GET", f"http://127.0.0.1:{PORT}/items?category=TOOLS")
    if status != 200 or len(body) != 2:
        errors.append(f"GET category filter (case-insensitive): got {len(body)} items, expected 2")

    # 5. GET /items?limit=1
    status, body = req("GET", f"http://127.0.0.1:{PORT}/items?limit=1")
    if status != 200 or len(body) != 1:
        errors.append(f"GET limit=1: got {len(body)} items, expected 1")

    # 6. GET /items/1
    status, body = req("GET", f"http://127.0.0.1:{PORT}/items/1")
    if status != 200 or body.get("name") != "Widget":
        errors.append(f"GET /items/1: got {status} {body}")

    # 7. GET /items/999 (nonexistent)
    status, body = req("GET", f"http://127.0.0.1:{PORT}/items/999")
    if status != 404:
        errors.append(f"GET /items/999: got {status}, expected 404")

    # 8. DELETE /items/2
    status, body = req("DELETE", f"http://127.0.0.1:{PORT}/items/2")
    if status != 200 or body.get("deleted") != True:
        errors.append(f"DELETE /items/2: got {status} {body}")

    # 9. DELETE /items/999 (nonexistent)
    status, _ = req("DELETE", f"http://127.0.0.1:{PORT}/items/999")
    if status != 404:
        errors.append(f"DELETE /items/999: got {status}, expected 404")

    # 10. Verify deletion worked
    status, body = req("GET", f"http://127.0.0.1:{PORT}/items")
    if len(body) != 1:
        errors.append(f"GET after delete: got {len(body)} items, expected 1")

finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

TOTAL = 10
passed = TOTAL - len(errors)
print(f"SCORE: {passed}/{TOTAL}")
if errors:
    print(f"FAIL ({len(errors)} issue(s)):")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (all 10 API tests passed)")
