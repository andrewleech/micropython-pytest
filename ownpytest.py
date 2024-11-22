import os
import sys


fixtures_mapping = {}


def get_traceback(ex):
    buf = io.StringIO()
    if hasattr(sys, "print_exception"):
        sys.print_exception(ex, buf)
    else:
        import traceback
        traceback.print_exception(None, ex, None, file=buf)
    return buf.getvalue()


def import_module(mod_path):
    mods = mod_path.split(".")
    mod = __import__(mod_path)
    while len(mods) > 1:
        mod = getattr(mod, mods.pop(1))
    return mod


def getmembers(object, predicate=None):
    names = dir(object)
    members = [(n, getattr(object, n)) for n in names]
    if predicate:
        members = [(n, o) for n, o in members if predicate(o)]
    return members


def get_test_files():
    for dr in os.listdir(sys.path[0]):
        if dr != "tests":
            continue
        for files in os.listdir(dr):
            if not (files.startswith("test") and files.endswith(".py")):
                continue
            yield dr + "." + files[:-3]


def get_test_functions(file_path):
    module = import_module(file_path)
    for members in sorted(getmembers(module, callable)):
        if members[0].startswith("test_"):
            yield members


def test_runner():
    errors = {}
    # get folder starts with tests in the current python path
    for files in get_test_files():
        for test_function_name, test_function_object in get_test_functions(files):
            test_args = test_function_object.__code__.co_varnames
            # Run the tests here
            print("Running test: ", test_function_name)

    if errors:
        print("\n------------------------ Errors -----------------------------------")
    else:
        print("\n------------- Success (No errors found) ---------------------------")


class raises:
    def __init__(self, exception):
        self.exception = exception

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, self.exception):
            return True
        else:
            raise AssertionError(f"Expected {self.exception}, got {exc_val}")


def parametrize(keys, values):
    # keys = "test_input,expected"
    # values = [("3+5", 8), ("2+4", 6), ("6*9", 54)]
    # output = [{"test_input": "3+5", "expected": 8},
    #  {"test_input": "2+4", "expected": 6},
    # {"test_input": "6*9", "expected": 54}]
    def decorator(func):

        # the function, to run subtests
        def wrapper(*args, **kwargs):
            pass

        return wrapper

    return decorator


def fixture(function):
    def fixture_wrapper():
        return function()

    return fixture_wrapper


if __name__ == "__main__":
    test_runner()
