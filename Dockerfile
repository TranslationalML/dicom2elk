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
COPY setup.py setup.cfg README.md get_version.py Makefile ./

# Install dicom2elk with static version taken from the argument
ARG VERSION=unknown 
RUN echo "${VERSION}" > /app/dicom2elk/VERSION
RUN pip install -e .[test] \
    && pip install pytest-order

###############################################################################
# Entrypoint
###############################################################################

# Create entrypoint to run dicom2elk executable script in dicom2elk environment
ENTRYPOINT ["micromamba", "run", "-n", "base", "dicom2elk"]

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
