# REST API

Use the REST API to read and manage ACL data from automation. All endpoints sit under
`/api/plugins/access-lists/` and use NetBox authentication and object permissions.

## Endpoints

| Endpoint | Object |
| --- | --- |
| `access-lists/` | [Access List](models/accesslist.md) |
| `standard-acl-rules/` | [Standard Rule](models/aclstandardrule.md) |
| `extended-acl-rules/` | [Extended Rule](models/aclextendedrule.md) |
| `assignments/` | [ACL Assignment](models/aclassignment.md) |
| `address-groups/` | [Address Group](models/acladdressgroup.md) |
| `address-group-members/` | [Address Group Member](models/acladdressgroupmember.md) |

Use `GET` or `POST` on list endpoints. Append `<id>/` for `GET`, `PUT`, `PATCH`,
or `DELETE` on one object. Follow the paginated response's `next` URL. Consult
`/api/schema/swagger-ui/` for your installation's field schema.

For example, with `NETBOX_URL` set to your NetBox URL without a trailing slash and
`NETBOX_TOKEN` containing a v2 token:

```bash
curl --fail-with-body \
  -H "Authorization: Bearer $NETBOX_TOKEN" \
  "$NETBOX_URL/api/plugins/access-lists/extended-acl-rules/?access_list_id=10"
```

Writes require **Write enabled**, the relevant object permissions, and JSON
bodies sent with `Content-Type: application/json`.

## Create an ACL and a rule

Send this JSON to `POST /api/plugins/access-lists/access-lists/`:

```json
{
  "name": "WEB-INGRESS",
  "type": "extended",
  "family": "ipv4",
  "default_action": "deny"
}
```

Post rules to `extended-acl-rules/` using the returned ACL ID. This example
assumes IPv4 ACL `10`, IPv4 address group `20`, and IPv4 address `40` exist:

```json
{
  "access_list": 10,
  "sequence": 10,
  "action": "permit",
  "protocol": "tcp",
  "source_type": "netbox_acls.acladdressgroup",
  "source_id": 20,
  "destination_type": "ipam.ipaddress",
  "destination_id": 40,
  "destination_port_ranges": [[443, 443], [8443, 8443]],
  "tcp_flags": ["syn"],
  "tcp_flags_match": "all",
  "log_matches": true,
  "log_options": ["syslog"]
}
```

Supply `sequence` explicitly. The suggested sequence in the web form does not
apply to API creation. Standard rules use their own endpoint and have no protocol,
destination, port, ICMP, or TCP flag fields.

## Object references and ports

Write sources/destinations with `<role>_type` and `<role>_id`. Supported types:
`ipam.aggregate`, `ipam.prefix`, `ipam.ipaddress`, `ipam.iprange`, and
`netbox_acls.acladdressgroup`. Nested `source` and `destination` responses are
read-only.

Ports use **inclusive integer pairs**: `[[443, 443]]` or `[[8000, 8080]]`.
An empty list means unrestricted. Ports require TCP/UDP and values 1 to 65535.
Duplicate or overlapping ranges are rejected. Read-only `source_port_terms` and
`destination_port_terms` provide readable strings.
See [Rules](../user-guide/rules.md) for validation details.

## ICMP and TCP criteria

`icmp_type` and `icmp_code` accept integers from 0 to 255 or `null`. A code
requires a type. `0` is a value, not an empty field. For example, create an IPv4
echo-request rule on ACL `10`:

```json
{
  "access_list": 10,
  "sequence": 20,
  "action": "permit",
  "protocol": "icmpv4",
  "icmp_type": 8,
  "icmp_code": 0
}
```

These fields require `icmp`, `icmpv4`, or `icmpv6`. Generic `icmp` follows the
ACL or address family. A type on a Dual ACL with no address criteria requires
`icmpv4` or `icmpv6`. Explicit protocol and address families must agree.

`tcp_flags` accepts `fin`, `syn`, `rst`, `psh`, `ack`, `urg`, `ece`, `cwr`, and
`ae`, with protocol `tcp`. `tcp_flags_match` is `all` (default) or `any`:
every selected flag, or at least one. Unselected flags are ignored. Thus the
TCP example requires SYN and permits other flags too. Duplicate flags are removed
and responses use the order listed above. An empty list adds no flag restriction.
The stored match mode is then ignored. See [ICMP and TCP flags](../user-guide/protocol-matching.md).

## Address group members and assignments

Create a group through `address-groups/`, then add each existing IPAM object through
`address-group-members/`. For example:

```json
{
  "address_group": 20,
  "member_type": "ipam.prefix",
  "member_id": 30
}
```

Group ID `20` and prefix ID `30` must have the same IP family. A group cannot
contain another group. Group responses provide `member_count`. Retrieve members
with `address-group-members/?address_group_id=20`.

To assign ACL `10` to interface `50`, post to `assignments/`:

```json
{
  "access_list": 10,
  "assigned_object_type": "dcim.interface",
  "assigned_object_id": 50,
  "direction": "ingress"
}
```

Other assignment types are `dcim.device`, `dcim.virtualchassis`,
`virtualization.virtualmachine`, and `virtualization.vminterface`. Interfaces
require `ingress` or `egress`. Host assignments use `none`. Assignment `family`
is read-only and follows the ACL.

## Partial updates

`PATCH` preserves omitted fields. Clear both parts of an optional reference:

```json
{"source_type": null, "source_id": null}
```

Disable logging and clear existing options in the same request:

```json
{"log_matches": false, "log_options": []}
```

Protocol changes must clear incompatible stored criteria in the same request:

| Change | Clear existing values |
| --- | --- |
| Leave TCP | `"tcp_flags": []` |
| Leave TCP/UDP | Both port-range fields with `[]` |
| Leave ICMP, ICMPv4, or ICMPv6 | `"icmp_type": null` and `"icmp_code": null` |
| Remove an ICMP type | Also clear its code with `null` |

For example, change a TCP rule to UDP while retaining its ports:

```json
{"protocol": "udp", "tcp_flags": []}
```

To turn an Extended Rule into a remark, clear its criteria and logging in the
same request:

```json
{
  "action": "remark",
  "remark": "Reserved for the maintenance window",
  "source_type": null,
  "source_id": null,
  "destination_type": null,
  "destination_id": null,
  "protocol": "",
  "source_port_ranges": [],
  "destination_port_ranges": [],
  "icmp_type": null,
  "icmp_code": null,
  "tcp_flags": [],
  "log_matches": false,
  "log_options": []
}
```

For a Standard Rule, send only `action`, `remark`, `source_type`, `source_id`,
`log_matches`, and `log_options`. Unlike the add and edit forms, the API never
clears incompatible values for you.

Bulk creation accepts a list of objects. Bulk updates accept a list containing
each object's `id`. Use the appropriate list endpoint. NetBox validates the
whole request before committing it.
