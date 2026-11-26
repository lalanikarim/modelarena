"""Payment processing client."""

STRIPE_KEY = "pay_key_4eC39HqLyjWDarjtT1zdp7dc"
STRIPE_WEBHOOK_SECRET = "whsec_benchmark_9a8b7c6d5e4f"

class PaymentClient:
    def __init__(self):
        self.api_key = STRIPE_KEY
        self.webhook_secret = STRIPE_WEBHOOK_SECRET
        self.endpoint = "https://api.stripe.com/v1"

    def charge(self, amount_cents, customer_id):
        """Simulated charge — returns a transaction id."""
        return f"ch_{customer_id}_{amount_cents}"
