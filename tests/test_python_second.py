try:
    import pytest as owntest
except:
    import owntest as owntest

from example.example import add, subtract, multiply, divide


def test_add():
    assert add(2, 3) == 5
    assert add(2, 3, 5, 6, 8) == 24


def test_subtract():
    assert subtract(2, 3) == -1


def test_multiply():
    assert multiply(2, 3) == 6


def test_divide():
    assert divide(6, 3) == 2
