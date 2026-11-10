# Filtering

Use list-page filters to find relevant objects. REST accepts the same filter
names as query parameters.

## Common filters

| Object | Useful filters |
| --- | --- |
| Access Lists | `name`, `type`, `family`, `default_action`, `description` |
| Both rule types | `access_list_id`, `sequence`, `action`, `source_type`, `source_id`, `log_matches`, `log_options` |
| Extended Rules | `protocol`, `destination_type`, `destination_id`, `source_port`, `destination_port` |
| Extended ICMP criteria | `icmp_type`, `icmp_code`, `icmp_type__empty`, `icmp_code__empty` |
| Extended TCP criteria | `tcp_flags`, `tcp_flags_match` |
| Assignments | `access_list_id`, `assigned_object_type`, `assigned_object_type_id`, `direction`, `family` |
| Address Groups | `name`, `family`, `description` |
| Address Group Members | `address_group_id`, `member_type`, `member_type_id`, `member_id` |

`access_list` and `address_group` use names. `_id` variants use numeric IDs.
Prefer IDs when ACL names repeat. Consult the API schema for additional NetBox
metadata filters.

Pair generic IDs such as `source_id`, `destination_id`, or `member_id` with their
object-type filter: the same numeric ID can exist in several object types.

## Rule references and ports

For either rule type, filter an exact source with `source_prefix_id`,
`source_aggregate_id`, `source_ipaddress_id`, `source_iprange_id`, or
`source_address_group_id`. Extended rules offer matching `destination_…` filters.

The variants without `_id` use a prefix, address, IP range start address, or group
name, as appropriate. These identify referenced objects. They do not calculate
which ACLs match a packet or expand address group members.

For example:

```text
/api/plugins/access-lists/extended-acl-rules/?access_list_id=10&protocol=tcp&destination_port=443
/api/plugins/access-lists/standard-acl-rules/?source_address_group_id=20
/api/plugins/access-lists/address-group-members/?member_type=ipam.prefix&member_id=30
```

Port filters find explicit ranges containing that port. A rule with an empty port
list has no port restriction, but is not included by `destination_port=443`.

Repeat a choice parameter to match any selected value:

```text
?action=permit&action=deny
?protocol=tcp&protocol=udp
?family=ipv4&family=dual
```

Different parameters combine to narrow the result. Repeated `log_options`
values match rules carrying any of those options.

## ICMP and TCP criteria

`icmp_type=0` selects that numeric type. `icmp_type__empty=true` selects an unset
type. The same applies to `icmp_code`. Protocol filters match stored choices:
`icmpv4` excludes generic `icmp` rules, even within an IPv4 ACL.

```text
/api/plugins/access-lists/extended-acl-rules/?access_list_id=10&protocol=icmpv4&icmp_type=8&icmp_code=0
/api/plugins/access-lists/extended-acl-rules/?icmp_type__empty=true
/api/plugins/access-lists/extended-acl-rules/?protocol=tcp&tcp_flags=ack&tcp_flags=rst&tcp_flags_match=any
```

Repeated `tcp_flags` values find rules containing **any** listed flag, independent
of their `all`/`any` mode. Filter the stored mode with `tcp_flags_match`, including
rules with empty flag lists. These filters inspect data. See
[ICMP and TCP flags](../user-guide/protocol-matching.md) for packet criteria and
[GraphQL](graphql.md#filter-protocol-criteria) for its filter input format.

## Assignment location and targets

`site`, `region`, and `site_group` accept slugs. `site_id`, `region_id`, and
`site_group_id` accept numeric IDs. Region and site-group filters include
descendants. Location is taken from the assigned device or VM, an interface's
parent, or a virtual chassis's master device.

```text
/api/plugins/access-lists/assignments/?region=europe&direction=ingress
/api/plugins/access-lists/assignments/?site_id=12&assigned_object_type=dcim.interface
```

Numeric values in the older bare location parameters remain accepted when no
matching slug exists. Use the explicit `_id` form for new integrations.

Target filters include `device_id`, `interface_id`, `virtual_chassis_id`,
`virtual_machine_id`, and `vminterface_id`, with corresponding name variants.
They select assignments to that object type. For example, `device_id` does not
also select its interface assignments. Use a location filter or query the relevant
interfaces separately.

## Search

The `q` parameter searches relevant names, descriptions, comments, and remarks.
For rules, an integer also matches the exact sequence number: `q=10` can match
sequence 10, while the numeric sequence match does not include 100.
