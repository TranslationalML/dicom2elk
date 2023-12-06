#!/bin/bash

# Copyright (C) 2023, The TranslationalML team and Contributors, All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

echo "Running pytest with coverage"
echo "Arguments: ${@}"

micromamba run -n base pytest \
    --cov-config "/app/.coveragerc" \
    --cov-report html:"/tests/report/cov_html" \
    --cov-report xml:"/tests/report/cov.xml" \
    --cov-report lcov:"/tests/report/cov.info" \
    --cov=dicom2elk \
    -s \
    "${@}"
