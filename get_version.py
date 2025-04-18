#!/usr/bin/env python

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

"""Utility script to get the version of `dicom2elk`."""

import sys
import os.path as op


def main():
    sys.path.insert(0, op.abspath("."))
    from dicom2elk.info import __version__

    print(__version__)
    return __version__


if __name__ == "__main__":
    main()
