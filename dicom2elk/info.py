# Copyright (C) 2023, The TranslationalML team and Contributors, All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""This file contains dicom2elk package information."""

import datetime


__version__ = "0.1.1dev"

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
