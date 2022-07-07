PLUGIN_NAME=netbox_access_lists
REPO_PATH=/opt/netbox/netbox/netbox-access-lists
VENV_PY_PATH=/opt/netbox/venv/bin/python3
NETBOX_MANAGE_PATH=/opt/netbox/netbox/manage.py
VERFILE=./version.py

.PHONY: help
help: ## Display help message
	@grep -E '^[0-9a-zA-Z_-]+\.*[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#################
#     DOCKER    #
#################

# Outside of Devcontainer

.PHONY: cleanup
cleanup: ## Clean associated docker resources.
	-docker-compose -p netbox-access-lists_devcontainer rm -fv

##################
#   PLUGIN DEV   #
##################

# in VS Code Devcontianer

.PHONY: setup
setup: ## Copy plugin settings.  Setup NetBox plugin.
	-${VENV_PY_PATH} -m pip install --disable-pip-version-check --no-cache-dir -e ${REPO_PATH}
#-python3 setup.py develop

.PHONY: makemigrations
makemigrations: ## Run makemigrations
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH} makemigrations --name ${PLUGIN_NAME}

.PHONY: migrate
migrate: ## Run migrate
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH} migrate

.PHONY: startup_scripts
startup_scripts:
	-echo "import runpy; runpy.run_path('/opt/netbox/startup_scripts')" | ${NETBOX_MANAGE_PATH} shell --interface python

.PHONY: collectstatic
collectstatic:
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH} collectstatic --no-input

.PHONY: start
start: ## Start NetBox
	-${VENV_PY_PATH} ${NETBOX_MANAGE_PATH} runserver

.PHONY: all
all: setup makemigrations migrate collectstatic startup_scripts start ## Run all PLUGIN DEV targets

#.PHONY: test
#test:
#	${VENV_PY_PATH} /opt/netbox/netbox/manage.py runserver test ${PLUGIN_NAME}

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
