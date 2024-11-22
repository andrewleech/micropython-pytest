import io
import os
import sys


fixtures_mapping = {}

def fixtures_available():
    return hasattr(fixtures_available, "__code__")


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
    dr = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    for fname in sorted(os.listdir(dr)):
        if not (fname.startswith("test") and fname.endswith(".py")):
            continue
        yield f"{dr}/{fname}", f"{dr}.{fname[:-3]}"


def get_test_functions(file_path):
    module = import_module(file_path)
    for members in sorted(getmembers(module, callable)):
        if members[0].startswith("test_"):
            yield members
        elif "fixture_wrapper" in members[1].__name__:
            fixtures_mapping[members[0]] = members[1]


def run_test(
    test_function_name, 
    test_function_object, 
    args,
    kwargs,
    passed,
    skipped,
    errors,
):
    try:
        test_function_object(*args, **kwargs)
        passed.append(test_function_name)
        print(".", end="")
    except ParamResults as res:
        p, s, e = res.args[0]
        passed.extend(p)
        skipped.extend(s)
        errors.update(e)
    except Skipped:
        skipped.append(test_function_name)
        print("s", end="")
    except Exception as err:
        errors[test_function_name] = get_traceback(err)
        print("F", end="")


def test_runner():
    overall_passed = []
    overall_skipped = []
    overall_errors = {}

    for path, module in get_test_files():
        heading = path

        passed = []
        skipped = []
        errors = {}

        for test_function_name, test_function_object in get_test_functions(module):
            test_function_ident = f"{path}::{test_function_name}"
            if heading:
                print(f"\n{heading} ", end="")
                heading = ""

            try:
                test_args = test_function_object.__code__.co_varnames
            except AttributeError as ex:
                if fixtures_mapping:
                    print("Error: Fixtures require micropython built with settrace enabled.")
                    raise SystemExit()
                test_args = []

            # Run the tests here
            test_args_to_pass = []
            for arg in test_args:
                if arg in fixtures_mapping:
                    fixture_return_value = fixtures_mapping[arg]()
                    # check if generator
                    if hasattr(fixture_return_value, "__next__"):
                        print("yielding generator")
                        test_args_to_pass.append(next(fixture_return_value))
                        print("after yielding generator")
                    else:
                        test_args_to_pass.append(fixture_return_value)
                else:
                    test_args_to_pass.append(arg)
                
            run_test(
                test_function_ident,
                test_function_object,
                test_args_to_pass,
                {},
                passed,
                skipped,
                errors,
            )

        overall_passed.extend(passed)
        overall_skipped.extend(skipped)
        overall_errors.update(errors)

    if overall_errors:
        print("\n\n====================== FAILURES ======================")
        for error_test_name, err in overall_errors.items():
            print(f"\nFAILED {error_test_name} failed with error:\n{err}")

    detail = ""
    if overall_errors:
        detail += f"{len(overall_errors)} failed, "    
    detail += f"{len(overall_passed)} passed"
    if overall_skipped:
        detail += f", {len(overall_skipped)} skipped"
    print(f"\n====================== {detail} ======================")
    
    if errors:
        return 1
    else:
        return 0


class raises:
    def __init__(self, exception):
        self.exception = exception

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):

        if exc_type is None:
            raise AssertionError(f"{self.exception} not raised")
        if exc_type is not self.exception:
            raise AssertionError(
                f"expected={self.exception} got \n {get_traceback(exc_val)}"
            ) from exc_val
        return True


def fixture(function):
    def fixture_wrapper():
        # doesn't support yielding functions
        return function()

    return fixture_wrapper


def skip(reason=""):
    raise Skipped(reason)


class mark:
    @staticmethod
    def parametrize(keys, values):
        def decorator(func):
            params = []
            for value in values:
                params.append(dict(zip([k.strip() for k in keys.split(",")], value)))
            # the function, to run subtests
            def _parametrize_wrapper(*args, **kwargs):
                """Runs the original test function with multiple params"""
                passed = []
                skipped = []
                errors = {}

                for i, param in enumerate(params):
                    # print(f"Running subtest {func.__name__}", i + 1)
                    run_test(
                        f"{func.__name__}:{i}",
                        func,
                        [],
                        param,
                        passed,
                        skipped,
                        errors,
                    )
                
                raise ParamResults((passed, skipped, errors))

            return _parametrize_wrapper

        return decorator

    @staticmethod
    def skip(reason):
        def decorator(function):
            def skip_wrapper(*args, **kwargs):
                raise Skipped(reason)

            return skip_wrapper
        return decorator
    
    @staticmethod
    def skipIf(test, reason=""):
        def decorator(function):
            if test:
                return mark.skip(reason)(function)
            return function
        return decorator


class ParamResults(Exception):
    pass

class Skipped(Exception):
    pass

class SubtestResults(Exception):
    pass

if __name__ == "__main__":
    sys.exit(test_runner())
