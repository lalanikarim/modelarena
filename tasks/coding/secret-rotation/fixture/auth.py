"""Authentication service (JWT)."""

JWT_SECRET = "a8f3k2m9x7q1v5b4n6z0w8e2r4t6y1u3i5o7p9s"
JWT_ISSUER = "app.internal.prod"
JWT_EXPIRY_HOURS = 24

class AuthService:
    def __init__(self):
        self.jwt_secret = JWT_SECRET
        self.issuer = JWT_ISSUER
        self.expiry_hours = JWT_EXPIRY_HOURS

    def sign_token(self, user_id):
        """Simulated JWT signing."""
        return f"eyJhbGciOi.{user_id}.{self.jwt_secret[:8]}"
