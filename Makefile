PLUGIN_NAME=netbox_acls
REPO_PATH=/opt/netbox/netbox/netbox-acls
VENV_PY_PATH=/opt/netbox/venv/bin/python3
NETBOX_MANAGE_PATH=/opt/netbox/netbox
NETBOX_INITIALIZER_PATH=${NETBOX_MANAGE_PATH}/netbox_initializers/
VERFILE=./version.py

.PHONY: help ## Display help message
help:
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

##################
##     DOCKER    #
##################
#
## Outside of Devcontainer
#
#.PHONY: cleanup ## Clean associated docker resources.
#cleanup:
#	-docker-compose -p netbox-acls_devcontainer rm -fv

##################
#   PLUGIN DEV   #
##################

# in VS Code Devcontianer

.PHONY: nbshell ## Run nbshell
nbshell:
	${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py nbshell
	from netbox_acls.models import *

.PHONY: setup ## Copy plugin settings.  Setup NetBox plugin.
setup:
	-${VENV_PY_PATH} -m pip install --disable-pip-version-check --no-cache-dir -e ${REPO_PATH}
#-python3 setup.py develop

.PHONY: example_initializers ## Run initializers
example_initializers:
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py copy_initializers_examples --path /opt/netbox/netbox/netbox-acls/.devcontainer/initializers

.PHONY: load_initializers ## Run initializers
load_initializers:
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py load_initializer_data  --path /opt/netbox/netbox/netbox-acls/.devcontainer/initializers

.PHONY: makemigrations ## Run makemigrations
makemigrations:
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py makemigrations --name ${PLUGIN_NAME}

.PHONY: migrate ## Run migrate
migrate:
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py migrate

.PHONY: collectstatic
collectstatic:
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py collectstatic --no-input

.PHONY: initializers
initializers:
	-rm -rf ${NETBOX_INITIALIZER_PATH}
	-mkdir ${NETBOX_INITIALIZER_PATH}
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py copy_initializers_examples --path ${NETBOX_INITIALIZER_PATH}
	-for file in ${NETBOX_INITIALIZER_PATH}/*.yml; do sed -i "s/^# //g" "$$file"; done
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH}/manage.py load_initializer_data --path ${NETBOX_INITIALIZER_PATH}

.PHONY: start ## Start NetBox
start:
	- cd /opt/netbox/netbox/ && /opt/netbox/docker-entrypoint.sh && /opt/netbox/launch-netbox.sh

.PHONY: all ## Run all PLUGIN DEV targets
all: setup makemigrations migrate collectstatic initializers start

.PHONY: rebuild ## Run PLUGIN DEV targets to rebuild
rebuild: setup makemigrations migrate collectstatic start

.PHONY: test
test: setup
	${NETBOX_MANAGE_PATH}/manage.py makemigrations ${PLUGIN_NAME} --check
	coverage run --source "netbox_acls" ${NETBOX_MANAGE_PATH}/manage.py test ${PLUGIN_NAME} -v 2

.PHONY: coverage_report
coverage_report:
	coverage report

.PHONY: test_coverage
test_coverage: test coverage_report

#relpatch:
#	$(eval GSTATUS := $(shell git status --porcelain))
#ifneq ($(GSTATUS),)
#	$(error Git status is not clean. $(GSTATUS))
#endif
#	git checkout develop
#	git remote update
#	git pull origin develop
#	$(eval CURVER := $(shell cat $(VERFILE) | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'))
#	$(eval NEWVER := $(shell pysemver bump patch $(CURVER)))
#	$(eval RDATE := $(shell date '+%Y-%m-%d'))
#	git checkout -b release-$(NEWVER) origin/develop
#	echo '__version__ = "$(NEWVER)"' > $(VERFILE)
#	git commit -am 'bump ver'
#	git push origin release-$(NEWVER)
#	git checkout develop

#pbuild:
#	${VENV_PY_PATH} -m pip install --upgrade build
#	${VENV_PY_PATH} -m build
#
#pypipub:
#	${VENV_PY_PATH} -m pip install --upgrade twine
#	${VENV_PY_PATH} -m twine upload dist/*
