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

"""Module for miscellaneous functions."""


def prepare_file_list_batches(file_list: list, batch_size: int):
    """Prepare batches of dicom files to process.

    Args:
        file_list (list): List of files to process.
        batch_size (int): Batch size.

    Returns:
        list: List of batches of files to process.
    """
    file_list_batches = []
    if len(file_list) == 0:
        return file_list_batches
    if batch_size > len(file_list):
        batch_size = len(file_list)
    for i in range(0, len(file_list), batch_size):
        file_list_batches.append(file_list[i : i + batch_size])
    return file_list_batches
