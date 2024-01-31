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

"""Tests for dicom2elk.utils.misc module."""

from dicom2elk.utils.misc import prepare_file_list_batches


def test_prepare_file_list_batches(test_dcm_files):
   # Prepare batches of dicom files to process
    dcm_list_batches = prepare_file_list_batches(test_dcm_files, 2)

    # Test if the batches are created correctly
    assert len(dcm_list_batches) == len(test_dcm_files) // 2
    assert dcm_list_batches[0] == test_dcm_files[:2]
    assert dcm_list_batches[1] == test_dcm_files[2:4]
    assert dcm_list_batches[2] == test_dcm_files[4:6]
    assert dcm_list_batches[3] == test_dcm_files[6:8]
