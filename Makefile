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

#test: @ Run all tests
.PHONY: test
test:
	@echo "Running pytest tests..."
	docker run -t --rm \
		--entrypoint "/entrypoint_pytest.sh" \
		-v $(PROJECT_DIR)/tests:/tests \
		-v $(PROJECT_DIR)/dicom2elk:/apps/dicom2elk/dicom2elk \
		-u $(USER_ID):$(GROUP_ID) \
		$(IMAGE_TAG) \
		/test
	@echo "Fix path in coverage xml report..."
	sed -i -r  \
		"s|/apps/datahipy/datahipy|$(PROJECT_DIR)/datahipy|g" \
		$(PROJECT_DIR)/test/report/cov.xml

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

#help:	@ List available tasks on this project
help:
	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
