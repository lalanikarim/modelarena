#!/usr/bin/env python3
"""Hidden oracle for config-migration: verifies complete migration to YAML."""
import subprocess, sys, os, json

errors = []
TOTAL = 10

# 1. config.json must be removed
if os.path.exists("config.json"):
    errors.append("config.json still exists — should be removed")

# 2. config.yaml must exist
if not os.path.exists("config.yaml"):
    errors.append("config.yaml does not exist")
else:
    # 3-7. Verify nested structure with correct values
    try:
        import yaml
        with open("config.yaml", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        
        # Check database section
        if cfg.get("database", {}).get("host") != "localhost":
            errors.append(f"database.host: expected 'localhost', got {cfg.get('database', {}).get('host')!r}")
        if cfg.get("database", {}).get("port") != 5432:
            errors.append(f"database.port: expected 5432, got {cfg.get('database', {}).get('port')!r}")
        if cfg.get("database", {}).get("name") != "app_db":
            errors.append(f"database.name: expected 'app_db', got {cfg.get('database', {}).get('name')!r}")
        
        # Check services.api section
        api = cfg.get("services", {}).get("api", {})
        if api.get("key") != "sk-legacy-abc123def456":
            errors.append(f"services.api.key: wrong value {api.get('key')!r}")
        if api.get("endpoint") != "https://api.example.com/v1":
            errors.append(f"services.api.endpoint: wrong value {api.get('endpoint')!r}")
        
        # Check logging section
        if cfg.get("logging", {}).get("level") != "INFO":
            errors.append(f"logging.level: expected 'INFO', got {cfg.get('logging', {}).get('level')!r}")
        if cfg.get("logging", {}).get("file") != "/var/log/app/server.log":
            errors.append(f"logging.file: wrong value {cfg.get('logging', {}).get('file')!r}")
    except ImportError:
        # PyYAML not installed — try to parse manually or use json as fallback check
        errors.append("PyYAML not available for verification; checking file content instead")
        with open("config.yaml", encoding="utf-8") as f:
            content = f.read()
        for expected in ["database:", "host:", "port:", "name:", "services:", "api:", "key:", "endpoint:", "logging:", "level:", "file:"]:
            if expected not in content:
                errors.append(f"config.yaml missing expected key/section: {expected}")
                break
    except Exception as e:
        errors.append(f"config.yaml parse error: {e}")

# 8-10. Run the test suite — all modules must work with new config
try:
    r = subprocess.run(
        [sys.executable, "tests/test_config.py"],
        capture_output=True, text=True, timeout=30, cwd="."
    )
    if r.returncode != 0:
        errors.append(f"test suite failed (exit {r.returncode}): {r.stdout.strip()[-300:]} {r.stderr.strip()[-200:]}")
    else:
        # Verify all 3 tests passed
        if "3/3" not in r.stdout:
            errors.append(f"test suite didn't report 3/3: {r.stdout.strip()[-200:]}")
except FileNotFoundError:
    errors.append("tests/test_config.py not found")
except subprocess.TimeoutExpired:
    errors.append("test suite timed out")

passed = TOTAL - len(errors)
print(f"SCORE: {passed}/{TOTAL}")
if errors:
    print(f"FAIL ({len(errors)} issue(s)):")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (migration complete, all tests green)")
