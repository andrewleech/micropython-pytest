try:
    import pytest as owntest
except:
    import ownpytest as owntest

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


def test_raises():
    with owntest.raises(TypeError):
        add("a", 3)

    with owntest.raises(TypeError):
        divide("a", 3)

    with owntest.raises(ZeroDivisionError):
        divide(6, 0)

    with owntest.raises(TypeError):
        multiply("a", 3)

    with owntest.raises(TypeError):
        subtract("a", 3)


@owntest.mark.parametrize("test_input, expected", [("3+5", 8), ("2+4", 6), ("6*9", 54), (None, None)])
def test_eval(test_input, expected):
    if not test_input:
        owntest.skip()
    assert eval(test_input) == expected


def test_fail():
    raise NotImplementedError("Should Fail")

@owntest.mark.skip("test_input")
def test_skip():
    raise NotImplementedError("Should not run this")


# if owntest.fixtures_available():
#     @owntest.fixture
#     def meaning_of_life():
#         return 42

#     @owntest.skipif
#     def test_meaning(meaning_of_life):
#         assert meaning_of_life == 41
