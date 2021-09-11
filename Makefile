PROJECT_NAME?=speedtest_youtube
#
DOCKER_TAG?=
#
# PYPI_SERVER?=https://tart.d-bi.fr/simple/
# https://stackoverflow.com/questions/2019989/how-to-assign-the-output-of-a-command-to-a-makefile-variable
PYPI_SERVER_HOST=$(shell echo $(PYPI_SERVER) | sed -e "s/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/")
PYTEST_OPTIONS?=-v
#
TOX_DIR?=${HOME}/.tox/speedtest_youtube/$(PROJECT_NAME)
#
SDIST_PACKAGE=dist/${shell python setup.py --fullname}.tar.gz
SOURCES=$(shell find src/ -type f -name '*.py') MANIFEST.in

all: docker

env: pyproject.toml poetry.lock poetry.toml
	@poetry install

re: fclean all

fclean:
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "__pycache__" -delete

test:
	@poetry run pytest -v

run-speedtest-youtube:
	@poetry run speedtest-youtube speedtest-youtube --show-progress-bar

run-speedtest-external:
	@poetry run speedtest-youtube speedtest-youtube-external

default: env
