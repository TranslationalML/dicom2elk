#!/bin/bash
CWD=$(dirname "$0")

pytest \
    -p no:cacheprovider \
    -s \
    "${CWD}/tests/test_profiling_lundin.py"
