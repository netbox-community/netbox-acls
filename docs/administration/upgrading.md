# Upgrading

Before upgrading, read the **Upgrade** notes in the [Release notes](../releases.md)
for every release between your installed version and the target.

## Before the upgrade

1. Confirm that your NetBox version supports the target plugin version, according
   to the [compatibility matrix](https://github.com/netbox-community/netbox-acls#compatibility).
2. Back up the NetBox database, configuration, and installed package versions.
3. Rehearse the upgrade on an isolated copy, especially when upgrading from
   an older plugin major version.
4. Arrange a maintenance window so web and worker processes use matching code
   and schema throughout the change.

## Upgrade the package and schema

Install the version the compatibility matrix lists for your NetBox, and update
its pin in `local_requirements.txt` if you use one. For a standard installation,
use NetBox's virtual environment:

```sh
source /opt/netbox/venv/bin/activate
python -m pip install --upgrade 'netbox-acls==<version>'
cd /opt/netbox/netbox
python manage.py migrate
python manage.py check
sudo systemctl restart netbox netbox-rq
```

For containers, rebuild and deploy the updated image using your normal
migration procedure.

After the upgrade, check access lists, rule ordering, assignments, and a
representative integration update.

## Older installations and recovery

The legacy migration chain includes a preflight check for invalid names,
missing assignment targets, and conflicting interface families. If it stops,
correct the reported records on the earlier schema before retrying. Do not
bypass it by marking migrations as applied.

Plan rollback around restoring a matching database backup and application
version. Some migrations refuse to reverse while data depends on the fields they
add, and a reversal deletes the data those migrations stored. The release notes
name these guards. To roll back without a backup, rehearse on a database copy,
then reverse the plugin's migrations with the newer version still installed and
install the older version.
