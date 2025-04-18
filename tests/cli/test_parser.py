# Copyright 2023-2024 Lausanne University and Lausanne University Hospital, Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for dicom2elk.cli.parser module."""

from dicom2elk.cli.parser import get_dicom2elk_parser, get_file2list_parser


def test_get_dicom2elk_parser():
    # Test if get_dicom2elk_parser returns a parser
    assert get_dicom2elk_parser() is not None


def test_get_file2list_parser():
    # Test if get_file2list_parser returns a parser
    assert get_file2list_parser() is not None
