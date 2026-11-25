"""Tests for the calculator module. The model must NOT modify these."""
import pytest
from calculator import (
    add, subtract, multiply, divide, mean, median, clamp, percentage
)


class TestArithmetic:
    def test_add(self):
        assert add(2, 3) == 5
        assert add(-1, 1) == 0

    def test_subtract(self):
        assert subtract(10, 4) == 6
        assert subtract(3, 7) == -4

    def test_multiply(self):
        assert multiply(3, 4) == 12
        assert multiply(-2, 5) == -10

    def test_divide(self):
        assert divide(10, 2) == 5
        with pytest.raises(ValueError):
            divide(1, 0)


class TestStatistics:
    def test_mean(self):
        assert mean([1, 2, 3, 4]) == 2.5
        with pytest.raises(ValueError):
            mean([])

    def test_median_odd(self):
        assert median([3, 1, 2]) == 2

    def test_median_even(self):
        # The two middle values are 2 and 3; median should be 2.5
        assert median([1, 2, 3, 4]) == 2.5

    def test_median_single(self):
        assert median([42]) == 42


class TestHelpers:
    def test_clamp(self):
        assert clamp(5, 0, 10) == 5
        assert clamp(-1, 0, 10) == 0
        assert clamp(15, 0, 10) == 10

    def test_percentage(self):
        assert percentage(25, 200) == 12.5
        with pytest.raises(ValueError):
            percentage(1, 0)
