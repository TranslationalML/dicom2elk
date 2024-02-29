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

.DEFAULT_GOAL := help

# Define the project directory
PROJECT_DIR = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Define the version tag 
TAG = $(shell python get_version.py)
$(info TAG = $(TAG))
# Replace +, /, _ with - to normalize the tag
# in case the tag includes a branch name
override TAG := $(subst +,-,$(TAG))
override TAG := $(subst /,-,$(TAG))
override TAG := $(subst _,-,$(TAG))
$(info TAG (Normalized) = $(TAG))

# Define the complete docker image tag 
IMAGE_TAG = $(if $(CI_REGISTRY),$(CI_REGISTRY)/ORG/dicom2elk:$(TAG),dicom2elk:$(TAG)) 

# Define the build date and vcs reference
BUILD_DATE = $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF = $(shell git rev-parse --short HEAD)

# Define the user and user id for the docker container
USER = $(shell whoami)
USER_ID = $(shell id -u $(USER))
GROUP_ID = $(shell id -g $(USER))

# Force to use buildkit for building the Docker image
export DOCKER_BUILDKIT=1

#tests: @ Run all tests
.PHONY: tests
tests:
	@echo "Running pytest tests..."
	docker run --rm \
		--entrypoint "/entrypoint_pytest.sh" \
		-v $(PROJECT_DIR)/tests:/tests \
		-v $(PROJECT_DIR)/dicom2elk:/app/dicom2elk \
		$(IMAGE_TAG) \
		/tests
	@echo "Fix path in coverage xml report..."
	sed -i -r  \
		"s|/app/dicom2elk|$(PROJECT_DIR)/dicom2elk|g" \
		$(PROJECT_DIR)/tests/report/cov.xml

#build-docker: @ Builds the Docker image
build-docker:
	docker build \
	-t $(IMAGE_TAG) \
	--build-arg BUILD_DATE=$(BUILD_DATE) \
	--build-arg VCS_REF=$(VCS_REF) \
	--build-arg VERSION=$(TAG) .

#install-python: @ Installs the python package
install-python:
	pip install .[all]

#install-python-wheel: @ Installs the python wheel
install-python-wheel: build-python-wheel
	pip install dicom2elk

#build-python-wheel: @ Builds the python wheel
build-python-wheel:
	python setup.py sdist bdist_wheel

#test-python-install: @ Tests the python package installation
test-python-install: install-python install-python-wheel	
	dicom2elk --version
	file2list --version

#help:	@ List available tasks on this project
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
