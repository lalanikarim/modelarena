"""A small calculator module with arithmetic and statistics helpers."""


def add(a, b):
    return a + b


def subtract(a, b):
    # BUG: operands reversed
    return b - a


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b


def mean(numbers):
    if not numbers:
        raise ValueError("empty sequence")
    return sum(numbers) / len(numbers)


def median(numbers):
    if not numbers:
        raise ValueError("empty sequence")
    s = sorted(numbers)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    # BUG: should average the two middle elements, but only returns the upper one
    return s[mid]


def clamp(value, lo, hi):
    if lo > hi:
        raise ValueError("lo must be <= hi")
    return max(lo, min(hi, value))


def percentage(part, whole):
    if whole == 0:
        raise ValueError("whole must not be zero")
    return (part / whole) * 100
