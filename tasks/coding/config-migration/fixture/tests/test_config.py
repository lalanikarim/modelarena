"""Tests that verify the app modules work correctly with the new config."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_db_connection():
    from db import get_connection
    conn = get_connection()
    assert "localhost" in conn, f"expected localhost in {conn}"
    assert "5432" in conn, f"expected 5432 in {conn}"
    assert "app_db" in conn, f"expected app_db in {conn}"

def test_api_client():
    from api_client import get_api_client
    client = get_api_client()
    assert client["key"] == "sk-legacy-abc123def456", f"wrong key: {client['key']}"
    assert client["endpoint"] == "https://api.example.com/v1", f"wrong endpoint: {client['endpoint']}"

def test_logging():
    from logging_setup import setup_logging
    log = setup_logging()
    assert log["level"] == "INFO", f"wrong level: {log['level']}"
    assert log["file"] == "/var/log/app/server.log", f"wrong file: {log['file']}"

if __name__ == "__main__":
    passed = 0
    failed = 0
    for name, fn in [("db_connection", test_db_connection), ("api_client", test_api_client), ("logging", test_logging)]:
        try:
            fn()
            print(f"PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {name}: {e}")
            failed += 1
    print(f"\n{passed}/{passed+failed} tests passed")
    sys.exit(0 if failed == 0 else 1)
