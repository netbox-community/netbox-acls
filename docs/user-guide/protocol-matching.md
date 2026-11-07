# ICMP and TCP flags

Use these criteria on **Extended Rules** when a protocol and address alone
do not describe the intended policy. Choose Permit or Deny, then select the
protocol to reveal its fields.

## Choose the ICMP family

| Protocol | When to use it |
|---|---|
| ICMP | Follow the ACL's family or the rule's address criteria. |
| ICMPv4 | Explicitly match IPv4 ICMP. |
| ICMPv6 | Explicitly match IPv6 ICMP. |

An explicit protocol must agree with the ACL and its addresses. For example,
ICMPv6 cannot be used in an IPv4 ACL or with an IPv4 source.

In a Dual ACL, a generic ICMP rule without addresses and without a type covers
both families. With a type, it needs a source or destination that determines
the family. For an Any-to-Any rule, choose **ICMPv4** or **ICMPv6** before
entering a type. An address group determines the family even when it has no
members.

## Select a type and code

**ICMP type** offers common message types and also accepts a number from
`0` to `255`. **ICMP code** accepts the same numeric range and requires a type.

- Leave both empty to match any ICMP type and code within the selected family.
- Set a type and leave code empty to match any code for that type.
- Set both to describe a specific message. `0` is a value, not an empty field.

In the add and edit forms, the presets follow the selected protocol. Generic
ICMP, bulk edit, and filters list both families with family labels.

A preset only fills in the type number. It changes neither the protocol nor the
family, and REST, GraphQL, and imports take the number directly.

Changing between ICMP variants keeps the entered type and code, so check their
meaning for the selected family before saving. The plugin validates the numeric
range, not whether a type and code combination is registered.

### Examples

| Intended traffic | Protocol | Type | Code |
|---|---|---|---|
| IPv4 echo request | ICMPv4 | `8` | `0` |
| IPv4 echo reply | ICMPv4 | `0` | `0` |
| IPv6 echo request | ICMPv6 | `128` | `0` |
| IPv6 neighbor solicitation | ICMPv6 | `135` | `0` |
| All IPv6 destination-unreachable messages | ICMPv6 | `1` | Empty |

Create separate rules when the IPv4 and IPv6 type numbers differ. ICMP rules
cannot include TCP/UDP ports or TCP flags.

## Select TCP flags

Choose **TCP**, select the flags, and choose a match mode:

| Mode | Meaning |
|---|---|
| All | Every selected flag must be set. This is the default. |
| Any | At least one selected flag must be set. |

Available flags are **FIN, SYN, RST, PSH, ACK, URG, ECE, CWR, and AE**.
Unselected flags are ignored, so the checks are positive only: **SYN** and
**ACK** with **All** require both bits set and say nothing about the others.
Selecting SYN alone therefore also matches SYN+ACK packets. An empty flag
selection adds no flag restriction, regardless of the mode.

**ACK** and **RST** with **Any** is the stateless established match. It
describes packets carrying either flag and does not track connections.

Flag criteria can be combined with TCP addresses and ports. The plugin does
not provide a separate `established` mode or criteria for requiring a flag to
be clear. Your automation translates these fields into device configuration.

See [Bulk operations](bulk-operations.md) for imports and bulk changes,
and [REST API](../reference/rest-api.md) for automation examples.
