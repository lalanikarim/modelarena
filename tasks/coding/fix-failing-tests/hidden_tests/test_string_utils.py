#!/usr/bin/env python3
"""Hidden oracle: all 8 test groups must pass."""
import subprocess, sys

TESTS = r'''
import sys
sys.path.insert(0, ".")
from string_utils import (
    reverse, is_palindrome, word_count, capitalize_words,
    truncate, remove_vowels, count_occurrences, is_anagram
)

errors = []

# 1. reverse
if reverse("hello") != "olleh": errors.append("reverse basic")
if reverse("") != "": errors.append("reverse empty")

# 2. is_palindrome — must ignore case AND non-alphanumeric
if not is_palindrome("racecar"): errors.append("palindrome simple")
if not is_palindrome("A man, a plan, a canal: Panama"):
    errors.append("palindrome: must ignore case and punctuation")

# 3. word_count
if word_count("hello world foo") != 3: errors.append("word_count normal")
if word_count("") != 0: errors.append("word_count empty")
if word_count("   ") != 0: errors.append("word_count whitespace")

# 4. capitalize_words — ALL words, not just first
if capitalize_words("hello world foo") != "Hello World Foo":
    errors.append(f"capitalize_words: got {capitalize_words('hello world foo')!r}, expected 'Hello World Foo'")

# 5. truncate — result length must include suffix within max_len
result = truncate("hello world", 8)
if len(result) > 8:
    errors.append(f"truncate: len={len(result)}, must be <= 8")
if not result.endswith("..."):
    errors.append(f"truncate: must end with '...', got {result!r}")

# 6. remove_vowels
if remove_vowels("hello") != "hll": errors.append("remove_vowels")

# 7. count_occurrences
if count_occurrences("banana", "a") != 3: errors.append("count_occurrences")

# 8. is_anagram — must be case-insensitive
if not is_anagram("listen", "silent"): errors.append("anagram basic")
if not is_anagram("Listen", "Silent"):
    errors.append("anagram: must be case-insensitive")

TOTAL = 14
passed = TOTAL - len(errors)
print(f"SCORE: {passed}/{TOTAL}")
if errors:
    print(f"FAIL ({len(errors)} issue(s)):")
    for e in errors: print(f"  {e}")
    sys.exit(1)
print("PASS (all functions correct)")
'''

r = subprocess.run([sys.executable, "-c", TESTS], capture_output=True, text=True, timeout=15)
print(r.stdout.strip())
if r.stderr.strip(): print(r.stderr.strip(), file=sys.stderr)
sys.exit(r.returncode)
