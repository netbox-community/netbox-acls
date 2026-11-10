# ACL Extended Rule

An `ACLExtendedRule` adds destination, protocol, ports, ICMP criteria, and TCP
flags to the fields shared with a [Standard Rule](aclstandardrule.md).
Its access list must have type `extended`.

## Additional fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `protocol` | Choice | No | `ip`, `icmp`, `icmpv4`, `icmpv6`, `tcp`, `udp`, `gre`, `eigrp`, `ospf`, or `pim`. Blank is allowed. |
| `destination_type`, `destination_id` | Content type and ID | No | Address object or group. Both unset means Any. |
| `source_port_ranges` | List of ranges | No | TCP/UDP only. Empty means any source port. |
| `destination_port_ranges` | List of ranges | No | TCP/UDP only. Empty means any destination port. |
| `icmp_type` | Integer or null | No | `0` to `255`. ICMP protocols only. Null means any type. |
| `icmp_code` | Integer or null | No | `0` to `255`. Requires a type. Null means any code for that type. |
| `tcp_flags` | List of choices | No | TCP only. Empty means no flag restriction. |
| `tcp_flags_match` | Choice | Default provided | `all` or `any`. Defaults to `all`. Ignored when flags are empty. |

Shared fields include `access_list`, `sequence`, `action`, `remark`, source,
logging, description, ownership, and NetBox metadata. Extended Rules do not
inherit an association with a Standard list.

## Ports

| Surface | Example for port 443 and ports 8000 to 8080 |
|---|---|
| Add/edit form | `443,8000-8080` |
| CSV import | A quoted cell: `"443,8000-8080"` |
| REST | `[[443, 443], [8000, 8080]]` |

Ranges are inclusive and must lie within `1` to `65535`. Overlapping ranges and
duplicate ports are rejected. Forms, bulk edit, and imports sort ranges and merge
adjacent ones. REST stores the ranges as sent. REST's
`source_port_terms` and `destination_port_terms` are read-only strings in a list.

## ICMP and TCP flags

ICMP type and code are numeric criteria. Zero is valid. The form's presets
are suggestions, and validation does not require a registered type/code pair.
Generic `icmp` follows the ACL or address family. `icmpv4` and `icmpv6` select
the family explicitly.

Flags are deduplicated and stored in TCP header bit order:
`fin`, `syn`, `rst`, `psh`, `ack`, `urg`, `ece`, `cwr`, `ae`.
`all` requires every selected flag. `any` requires at least one.
Unselected flags are ignored. ACK and RST with `any` describes a stateless
established match. No connection state is stored or checked.

These fields are also available in cloning, tables, filters, imports, bulk
editing, REST, and GraphQL. See [ICMP and TCP flags](../../user-guide/protocol-matching.md)
for usage examples.

## Validation

Source, destination, and an explicit ICMP protocol must agree with the list's
family. A Dual list still cannot have IPv4 and IPv6 criteria in the same rule.
A generic ICMP rule with a type in a Dual ACL requires an address criterion
that determines the family. Otherwise, choose `icmpv4` or `icmpv6`.

Ports require TCP or UDP. Flags require TCP. A Remark requires text and cannot
have a source, destination, protocol, ports, ICMP type/code, TCP flags, or
logging settings. On REST updates, clear incompatible values explicitly.
The add/edit form's automatic clearing is specific to that form.

## Access

| Surface | Path |
|---|---|
| UI | `/plugins/access-lists/extended-rules/` |
| REST | `/api/plugins/access-lists/extended-acl-rules/` |

See [Rules](../../user-guide/rules.md), [REST API](../rest-api.md), and
[Field choices](../choices.md).
