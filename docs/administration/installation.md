# Installation

Install NetBox ACLs in the same Python environment as NetBox. For an existing
installation, follow [Upgrading](upgrading.md).

## Requirements

Check the [compatibility matrix](https://github.com/netbox-community/netbox-acls#compatibility) for the plugin version that matches
your NetBox release. The plugin needs no services beyond your NetBox deployment.

## Install and enable

Activate NetBox's virtual environment and install the plugin:

```sh
source /opt/netbox/venv/bin/activate
python -m pip install netbox-acls
```

To install a specific version, pin it, for example
`python -m pip install 'netbox-acls==2.2.0'`. On an older NetBox release, pin the
version the compatibility matrix lists for it.

Add the same requirement to `/opt/netbox/local_requirements.txt` so NetBox's
upgrade process reinstalls it.

For NetBox Docker, add the package to the requirements used to build your image
and rebuild it. Follow the
[NetBox Docker plugin guide](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins)
for your deployment.

Add `netbox_acls` to `PLUGINS` in NetBox's configuration, preserving existing
entries:

```python
PLUGINS = [
    # Your existing plugins.
    "netbox_acls",
]
```

No additional settings are required. Optional settings are described in
[Configuration](configuration.md).

## Apply and verify

For a standard installation:

```sh
cd /opt/netbox/netbox
python manage.py migrate
python manage.py check
sudo systemctl restart netbox netbox-rq
```

Use the equivalent commands and restart procedure for containers or managed
deployments. Every NetBox process must load the same plugin version.

| Check | Expected result |
|---|---|
| Open NetBox's plugin list | **Access Lists** is listed. |
| Sign in with the appropriate permissions | The **Access Lists** menu is available. |
| Open `/api/plugins/access-lists/` | The plugin's REST API root responds. |

Configure [Permissions](permissions.md), then continue with
[Getting started](../user-guide/getting-started.md).
