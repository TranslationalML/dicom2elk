# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.cli.parser module."""

from dicom2elk.cli.parser import get_parser


def test_get_parser():
    # Test if get_parser returns a parser
    assert get_parser() is not None
