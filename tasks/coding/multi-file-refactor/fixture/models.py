"""Data models for the mini web service."""


class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    def __repr__(self):
        return f"User({self.username!r})"


# In-memory user store (would be a DB in production)
USERS = {
    "alice": User("alice", "alice@example.com"),
    "bob": User("bob", "bob@example.com"),
}


def get_user(username: str) -> User | None:
    return USERS.get(username)


def list_users() -> list[User]:
    return list(USERS.values())
