#!/bin/bash
CWD=$(dirname "$0")

pytest \
    --cov-config "${CWD}/.coveragerc" \
    --cov-report html:"${CWD}/tests/report/html" \
    --cov-report xml:"${CWD}/tests/report/coverage.xml" \
    --cov-report lcov:"${CWD}/tests/report/coverage.lcov" \
    --cov=dicom2elk \
    -p no:cacheprovider \
    -s \
    "${@}"
