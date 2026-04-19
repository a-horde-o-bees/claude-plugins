"""CLI alias — `ocd-run tests` dispatches to framework's test runner."""

import sys

from framework import test_runner_main

if __name__ == "__main__":
    sys.exit(test_runner_main())
