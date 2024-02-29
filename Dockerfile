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

###############################################################################
# Base image
###############################################################################
FROM mambaorg/micromamba:1.5.3

###############################################################################
# Basic setup
###############################################################################

# mambaorg/micromamba defaults to a non-root user. Add a "USER root" to install packages as root:
USER root

# Set working directory
WORKDIR /app

###############################################################################
# Create micromamba environment
###############################################################################

# Copy conda environment file and install environment with micromamba
COPY  conda/environment.yml environment.yml
RUN micromamba install --yes --name base -f environment.yml && \
     micromamba clean --all --yes

# Activate micromamba environment
ARG MAMBA_DOCKERFILE_ACTIVATE=1

###############################################################################
# Install dicom2elk
###############################################################################

# Copy project files
COPY dicom2elk/ dicom2elk/
COPY .coveragerc setup.py setup.cfg README.md get_version.py Makefile ./

# Install dicom2elk with static version taken from the argument
ARG VERSION=unknown 
RUN echo "${VERSION}" > /app/dicom2elk/VERSION
RUN pip install -e .[test] \
    && pip install pytest-order

###############################################################################
# Create initial folders for testing / code coverage with correct permissions
###############################################################################

# Create directories for reporting tests and code coverage
RUN mkdir -p "/tests/report" && chmod -R 775 "/tests"

###############################################################################
# Set environment variables
###############################################################################

# Set the environment variable for .coverage file
ENV COVERAGE_FILE="/tests/report/.coverage"

###############################################################################
# Configure the entrypoint scripts
###############################################################################

# Copy the pytest entrypoint script and make it executable
COPY scripts/entrypoint_pytest.sh /entrypoint_pytest.sh
RUN chmod +x /entrypoint_pytest.sh

# Create entrypoint to run dicom2elk executable script in dicom2elk environment
ENTRYPOINT ["micromamba", "run", "-n", "base"]

###############################################################################
# Container Image Metadata (label schema: http://label-schema.org/rc1/)
###############################################################################

ARG BUILD_DATE=today
ARG VCS_REF=unknown

LABEL org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="dicom2elk" \
    org.label-schema.description="Tool to convert DICOM files to JSON and send them to an ELK stack" \
    org.label-schema.url="https://translationalml.github.io/" \
    org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.vcs-url="https://github.com/TranslationalML/dicom2elk" \
    org.label-schema.version=${VERSION} \
    org.label-schema.maintainer="The TranslationalML team" \
    org.label-schema.vendor="The TranslationalML team" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.docker.cmd="TBC" \
    org.label-schema.docker.cmd.test="TBC"
