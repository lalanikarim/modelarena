#!/usr/bin/env python3
"""Main application entry point."""
import sys
from database import get_connection
from payments import PaymentClient
from notifications import NotificationService
from auth import AuthService

def check():
    """Verify all modules can initialize with their configured credentials."""
    errors = []

    try:
        conn = get_connection()
        if "localhost" not in conn and "postgres" not in conn:
            errors.append(f"database: unexpected connection string {conn[:30]}...")
    except Exception as e:
        errors.append(f"database: {e}")

    try:
        client = PaymentClient()
        if not client.api_key:
            errors.append("payments: API key is empty")
    except Exception as e:
        errors.append(f"payments: {e}")

    try:
        svc = NotificationService()
        if not svc.slack_token:
            errors.append("notifications: Slack token is empty")
    except Exception as e:
        errors.append(f"notifications: {e}")

    try:
        auth = AuthService()
        if not auth.jwt_secret:
            errors.append("auth: JWT secret is empty")
    except Exception as e:
        errors.append(f"auth: {e}")

    if errors:
        print("CHECK FAILED:")
        for e in errors:
            print(f"  {e}")
        return 1
    print("CHECK PASSED: all modules initialized successfully")
    return 0

if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else 0)
