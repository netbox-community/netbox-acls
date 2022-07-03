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
	-cp /opt/netbox/netbox/netbox-access-lists/plugins.py /etc/netbox/config/plugins.py
	-python3 setup.py develop

.PHONY: makemigrations
makemigrations: ## Run makemigrations
	-python3 /opt/netbox/netbox/manage.py makemigrations netbox_access_lists

.PHONY: migrate
migrate: ## Run migrate
	-python3 /opt/netbox/netbox/manage.py migrate

.PHONY: startup_scripts
startup_scripts:
	-echo "import runpy; runpy.run_path('/opt/netbox/startup_scripts')" | /opt/netbox/netbox/manage.py shell --interface python

.PHONY: collectstatic
collectstatic:
	-python3 /opt/netbox/netbox/manage.py collectstatic --no-input

.PHONY: start
start: ## Start NetBox
	-python3 /opt/netbox/netbox/manage.py runserver

.PHONY: all
all: setup makemigrations migrate collectstatic startup_scripts start ## Run all PLUGIN DEV targets
