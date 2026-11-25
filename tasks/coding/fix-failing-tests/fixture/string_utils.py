"""String utility functions."""


def reverse(s: str) -> str:
    return s[::-1]


def is_palindrome(s: str) -> bool:
    # BUG: doesn't ignore case or non-alphanumeric characters
    return s == s[::-1]


def word_count(s: str) -> int:
    # BUG: splits on all whitespace but doesn't handle empty string correctly
    # (actually this one is fine — the bug is elsewhere)
    if not s.strip():
        return 0
    return len(s.split())


def capitalize_words(s: str) -> str:
    # BUG: only capitalizes the first word, not all words
    if not s:
        return s
    return s[0].upper() + s[1:]


def truncate(s: str, max_len: int, suffix: str = "...") -> str:
    if len(s) <= max_len:
        return s
    # BUG: doesn't account for the suffix length in the truncation
    return s[:max_len] + suffix


def remove_vowels(s: str) -> str:
    vowels = "aeiouAEIOU"
    return "".join(c for c in s if c not in vowels)


def count_occurrences(s: str, char: str) -> int:
    return s.count(char)


def is_anagram(a: str, b: str) -> bool:
    # BUG: doesn't ignore case
    return sorted(a) == sorted(b)
