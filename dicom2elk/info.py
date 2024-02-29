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

"""This file contains dicom2elk package information."""

import datetime


__version__ = "0.1.1"

__current_year__ = datetime.datetime.now().strftime("%Y")

__release_date__ = "DD.MM.{}".format(__current_year__)

__author__ = "The TranslationalML team and Contributors"

__copyright__ = "\n".join(
    [
        "Copyright (C)".format(__current_year__),
        "The TranslationalML team and Contributors.",
        "All rights reserved.",
    ]
)

__credits__ = (
    "Contributors: please check the ``.zenodo.json`` file at the top-level folder"
    "of the repository"
)

__packagename__ = "dicom2elk"

__url__ = "https://github.com/TranslationalML/{name}/tree/{version}".format(
    name=__packagename__, version=__version__
)

DOWNLOAD_URL = "https://github.com/TranslationalML/{name}/archive/{ver}.tar.gz".format(
    name=__packagename__, ver=__version__
)

DOCKER_HUB = "TO_BE_COMPLETED_ONCE_IT_IS_DEPLOYED"
