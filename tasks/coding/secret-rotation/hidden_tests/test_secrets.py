#!/usr/bin/env python3
"""Hidden oracle for secret-rotation: verifies all secrets are externalized."""
import subprocess, sys, os, re

errors = []
TOTAL = 12

# Known secret values that must NOT appear in source files
SECRETS = {
    "xK9#mP2vLqR7nWz4": "DB password",
    "pay_key_4eC39HqLyjWDarjtT1zdp7dc": "Payment API key",
    "whsec_benchmark_9a8b7c6d5e4f": "Webhook secret",
    "slack_bot_token_AbCdEfGhIjKlMnOpQrSt": "Slack bot token",
    "EmailS3cure!2024": "SMTP password",
    "a8f3k2m9x7q1v5b4n6z0w8e2r4t6y1u3i5o7p9s": "JWT secret",
}

# 1-6: Each secret must not appear in any .py file
source_files = [f for f in os.listdir(".") if f.endswith(".py")]
for secret, label in SECRETS.items():
    found_in = []
    for sf in source_files:
        with open(sf, encoding="utf-8") as f:
            content = f.read()
        if secret in content:
            found_in.append(sf)
    if found_in:
        errors.append(f"{label} still hardcoded in: {', '.join(found_in)}")

# 7: .env.example must exist
if not os.path.exists(".env.example"):
    errors.append(".env.example file does not exist")
else:
    with open(".env.example", encoding="utf-8") as f:
        env_content = f.read()
    
    # 8-11: .env.example must reference all the required variables (by name pattern)
    required_patterns = [
        (r"DB_PASS", "database password variable"),
        (r"STRIPE", "Stripe API key variable"),
        (r"SLACK", "Slack token variable"),
        (r"(JWT|AUTH).*SECRET|SECRET.*(JWT|AUTH)", "JWT secret variable"),
    ]
    for pattern, label in required_patterns:
        if not re.search(pattern, env_content, re.IGNORECASE):
            errors.append(f".env.example missing {label} (pattern: {pattern})")

# 12: App must still work with env vars set
env = os.environ.copy()
# Set the env vars to the original values so the app can initialize
env["DB_PASSWORD"] = "xK9#mP2vLqR7nWz4"
env["DB_HOST"] = "db.internal.prod"
env["DB_PORT"] = "5432"
env["DB_USER"] = "app_service"
env["DB_NAME"] = "production_app"
env["STRIPE_API_KEY"] = "pay_key_4eC39HqLyjWDarjtT1zdp7dc"
env["STRIPE_WEBHOOK_SECRET"] = "whsec_benchmark_9a8b7c6d5e4f"
env["SLACK_BOT_TOKEN"] = "slack_bot_token_AbCdEfGhIjKlMnOpQrSt"
env["SMTP_PASSWORD"] = "EmailS3cure!2024"
env["JWT_SECRET"] = "a8f3k2m9x7q1v5b4n6z0w8e2r4t6y1u3i5o7p9s"

try:
    r = subprocess.run(
        [sys.executable, "app.py", "--check"],
        capture_output=True, text=True, timeout=15, env=env
    )
    if r.returncode != 0:
        errors.append(f"app.py --check failed (exit {r.returncode}): {r.stdout.strip()[-200:]} {r.stderr.strip()[-200:]}")
except FileNotFoundError:
    errors.append("app.py not found")
except subprocess.TimeoutExpired:
    errors.append("app.py --check timed out")

passed = TOTAL - len(errors)
print(f"SCORE: {passed}/{TOTAL}")
if errors:
    print(f"FAIL ({len(errors)} issue(s)):")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (all secrets externalized, app works)")
