# Rules

Rules describe the intended traffic policy in sequence order. Open an access
list and select **Add Rule**, or use **Standard Rules** or **Extended Rules**
from the Access Lists menu.

## Actions and sequence numbers

| Field | How to use it |
|---|---|
| Sequence | Position in the list. Each rule, including a remark, needs its own number. Leave gaps such as `10`, `20`, and `30` for later additions. |
| Permit | Allow traffic matching the criteria. |
| Deny | Drop traffic matching the criteria. |
| Remark | A comment-only entry. Enter a remark and leave traffic criteria and logging unset. |
| Remark text | An optional note on Permit or Deny rules, required for Remark rules. |

When you add a rule from its access list, NetBox suggests the next sequence
using the configured increment. It does not renumber existing rules. Imports
and API requests must supply a sequence explicitly.

## Match addresses

Select an aggregate, prefix, IP address, IP range, or address group. Standard
Rules have a source, and Extended Rules also have a destination.

Leave a source or destination empty to document **any address** in that role.
To allow an entire subnet, select a Prefix or Aggregate. An IP Address represents
the host address, even when NetBox displays it with a subnet mask.

Address criteria must match the list's family. Within a Dual list, an individual
rule may use IPv4 criteria or IPv6 criteria, but cannot combine them.

## Protocols and ports

Extended Rules support IP, ICMP, ICMPv4, ICMPv6, TCP, UDP, GRE, EIGRP, OSPF,
and PIM. Use **IP** for a rule without an upper-layer protocol restriction.
A blank protocol is stored as unspecified. Define its handling in your automation.

Only TCP and UDP allow ports. Enter numbers or inclusive ranges, separated
by commas:

```text
22,80-81,443,1024-65535
```

Ports must be between `1` and `65535`. Empty ports mean any port. Forms, bulk
edit, and imports sort ranges and combine adjacent ranges. Overlapping ranges,
including duplicate ports, are rejected.

ICMP rules can select a numeric type and code. TCP rules can select flags
with **All** or **Any** matching. See [ICMP and TCP flags](protocol-matching.md)
for examples and address-family requirements.

## Logging

Enable **Log matches** to record that the device should log matching traffic.
**Log options** are optional: Syslog and Cisco Log-input are built in.
Leave the options empty for the target platform's default logging behavior.
Options require Log matches to be enabled. Remark rules cannot request logging.

## Fields change with your selections

For Extended Rules, the add and edit forms show fields for the selected action
and protocol:

| Selection | Available criteria |
|---|---|
| Permit or Deny | Addresses, protocol, and logging. |
| TCP or UDP | Source and destination ports. |
| ICMP, ICMPv4, or ICMPv6 | ICMP type and code. |
| TCP | TCP flags and All/Any matching. |
| Remark | Remark text, with no traffic criteria or logging. |

Saving clears values that no longer apply. Changing TCP to GRE clears ports
and flags, and changing to Remark clears traffic criteria and logging. Switching
between ICMP variants keeps the numeric type and code, so review their meaning
for the selected family.

On an edit form, showing a field again restores its saved value. Unsaved changes
in fields that disappeared are not retained. See
[Limitations](../features.md#limitations) for emptied multi-select fields.

Bulk edit, imports, and the REST API preserve omitted fields and reject
incompatible values, so clear those explicitly. In bulk edit, setting
**Log matches** to **No** also clears the log options. See
[Bulk operations](bulk-operations.md) and the [REST API](../reference/rest-api.md).
