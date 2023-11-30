#!/usr/bin/env python

# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Utility script to get the version of `dicom2elk`."""

import sys
import os.path as op


def main():
    sys.path.insert(0, op.abspath("."))
    from dicom2elk import __version__

    print(__version__)
    return __version__


if __name__ == "__main__":
    main()
