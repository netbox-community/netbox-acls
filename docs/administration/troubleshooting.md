# Troubleshooting

Confirm the installed NetBox and plugin versions, then check the reported
symptom.

| Symptom | What to check |
|---|---|
| The plugin fails to load | Install it in NetBox's Python environment, enable `netbox_acls`, and check the [compatibility matrix](https://github.com/netbox-community/netbox-acls#compatibility). |
| The menu is missing | Check view permissions and `top_level_menu`. With `False`, look under **Plugins**. |
| A new model reports a missing database table | Run the release's migrations with the same code and configuration used by the web process. |
| An object is missing from a selector | Check its type, relevant filters, and the user's view permissions. |
| A reference tab is missing | Check the corresponding rule or member view permission. Empty reference tabs may be hidden. |
| An ACL's type or family cannot change | An ACL with rules keeps its type and family. Review the [Access List reference](../reference/models/accesslist.md). |
| An interface assignment conflicts | Check the direction and family. A Dual assignment occupies both IPv4 and IPv6 slots. |
| A port range is rejected | Port criteria require TCP or UDP. Use valid inclusive ranges and the format expected by the form or API. |
| ICMPv4 or ICMPv6 is missing | Review any custom protocol `FIELD_CHOICES` replacement in [Configuration](configuration.md#customized-protocol-choices). |
| An ICMP type is rejected | Use 0 to 255 with an ICMP protocol. A code requires a type. In a Dual ACL without address criteria, choose ICMPv4 or ICMPv6 before setting a type. See [ICMP and TCP flags](../user-guide/protocol-matching.md). |
| An API protocol change fails | Clear incompatible stored ports, ICMP fields, or TCP flags in the same request. Omitted fields are retained. See [REST API](../reference/rest-api.md). |
| An IPAM object or group cannot be deleted | Remove or replace its rule and membership references first. Review the objects listed by NetBox. |

## Check migrations

From NetBox's environment and the directory containing `manage.py`:

```sh
python manage.py showmigrations netbox_acls
python manage.py check
```

For upgrade failures, follow [Upgrading](upgrading.md) before changing migration
state. Rehearse upgrades on a database copy.

## Report an issue

Search the [issue tracker](https://github.com/netbox-community/netbox-acls/issues)
first. Include versions, reproduction steps, expected and actual behavior, and
error text. Remove credentials and private network details. Follow the
[security policy](https://github.com/netbox-community/netbox-acls/security/policy)
when reporting a vulnerability.
