# Features and limitations

## Features

| Area | What you can document |
|---|---|
| Access lists | Standard and Extended ACLs for IPv4, IPv6, or both, with a default action. |
| Standard Rules | Source address criteria, permit and deny actions, remarks, and logging intent. |
| Extended Rules | Source and destination criteria, IP protocols, TCP/UDP ports, ICMP types and codes, TCP flags, remarks, and logging intent. |
| Address groups | Reusable groups of aggregates, prefixes, IP addresses, and IP ranges. Each group has one address family. |
| Assignments | Device, virtual chassis, virtual machine, device interface, and VM interface associations. Interface assignments have an ingress or egress direction. |
| NetBox integration | Related-object tabs, object permissions, ownership, tags, custom fields, change logging, bulk operations, REST, and GraphQL. |

Add and edit forms show the fields relevant to the selected action, protocol,
and assignment target. See [Rules](user-guide/rules.md) for how changing those
selections affects saved values.

## Scope

NetBox ACLs stores intended policy. It does not generate or deploy device
configuration, enforce traffic policy, test packets, or detect shadowed and
redundant rules. Your automation must translate the recorded policy into the
target platform's syntax and supported behavior.

Address groups contain IPAM objects. Nested groups, service groups, and protocol
groups are not supported. Adding a prefix includes that prefix as one member.
It does not create memberships for the IP addresses inside it.

Assignments are explicit. A device or virtual chassis assignment does not create
interface assignments, and ACLs are not inherited by site, role, tag, or parent
object.

Logging options describe what a device should do. The plugin does not collect
packet logs. Vendor-specific options may need special handling in your automation.

## Limitations

Add and edit forms refresh when you change a controlling field, such as the
action or protocol, so that only the applicable fields show:

- A field that reappears on an edit form shows its saved value. Changes made to
  it before it was hidden are not kept.
- An emptied multi-select field, such as log options or tags, shows its saved
  selection again after a refresh. Review those fields before saving.

Saving the add or edit form clears the stored values of fields that no longer
apply. Bulk edit, imports, and the REST API preserve omitted fields and reject
incompatible values, so clear those explicitly. In bulk edit, setting
**Log matches** to **No** also clears the log options.
