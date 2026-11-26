"""Notification service (Slack + email)."""

SLACK_BOT_TOKEN = "slack_bot_token_AbCdEfGhIjKlMnOpQrSt"
SLACK_CHANNEL = "#deploy-alerts"
SMTP_PASSWORD = "EmailS3cure!2024"
SMTP_HOST = "smtp.internal.prod"

class NotificationService:
    def __init__(self):
        self.slack_token = SLACK_BOT_TOKEN
        self.channel = SLACK_CHANNEL
        self.smtp_host = SMTP_HOST
        self.smtp_password = SMTP_PASSWORD

    def notify_deploy(self, message):
        """Simulated Slack notification."""
        return f"posted to {self.channel}: {message}"
