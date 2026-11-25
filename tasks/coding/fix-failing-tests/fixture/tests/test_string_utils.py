"""Tests for string_utils. The model must NOT modify this file."""
import pytest
from string_utils import (
    reverse, is_palindrome, word_count, capitalize_words,
    truncate, remove_vowels, count_occurrences, is_anagram
)


class TestReverse:
    def test_basic(self):
        assert reverse("hello") == "olleh"

    def test_empty(self):
        assert reverse("") == ""


class TestPalindrome:
    def test_simple(self):
        assert is_palindrome("racecar") is True

    def test_case_and_punctuation(self):
        # "A man, a plan, a canal: Panama" is a palindrome ignoring case/punctuation
        assert is_palindrome("A man, a plan, a canal: Panama") is True


class TestWordCount:
    def test_normal(self):
        assert word_count("hello world foo") == 3

    def test_empty(self):
        assert word_count("") == 0
        assert word_count("   ") == 0


class TestCapitalizeWords:
    def test_all_words(self):
        assert capitalize_words("hello world foo") == "Hello World Foo"

    def test_already_capped(self):
        assert capitalize_words("Hello World") == "Hello World"


class TestTruncate:
    def test_no_truncation_needed(self):
        assert truncate("hi", 10) == "hi"

    def test_truncation_with_suffix(self):
        # Result should be at most max_len characters total
        result = truncate("hello world", 8)
        assert len(result) <= 8
        assert result.endswith("...")


class TestRemoveVowels:
    def test_basic(self):
        assert remove_vowels("hello") == "hll"


class TestCountOccurrences:
    def test_basic(self):
        assert count_occurrences("banana", "a") == 3


class TestIsAnagram:
    def test_basic(self):
        assert is_anagram("listen", "silent") is True

    def test_case_insensitive(self):
        assert is_anagram("Listen", "Silent") is True
