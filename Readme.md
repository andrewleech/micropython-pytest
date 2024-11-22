# micropython-pytest 

Lightweight implementation of pytest intended for use on micropython. 

## How to Run?
```
$ micropython -m pytest tests/

tests/test_python_basics.py .....sF..s.
tests/test_python_second.py ....

====================== FAILURES ======================

FAILED tests/test_python_basics.py::test_fail failed with error:
Traceback (most recent call last):
  File "pytest.py", line 65, in run_test
  File "tests/test_python_basics.py", line 48, in test_fail
NotImplementedError: Should Fail


====================== 1 failed, 12 passed, 2 skipped ======================
```

## Credits

Originally based on [ownpytest](https://github.com/bhavaniravi/ownpytest), for more information see:  
https://www.bhavaniravi.com/python/how-to-build-a-testing-library-like-pytest
