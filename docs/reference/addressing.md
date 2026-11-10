# Address references

Rules reference existing NetBox objects. They do not store free-form address
strings. Create an IPAM object or address group first, then select it.

## Supported objects

| Object | REST content type | Intended use |
|---|---|---|
| Aggregate | `ipam.aggregate` | An entire aggregate prefix. |
| Prefix | `ipam.prefix` | An entire network prefix. |
| IP Address | `ipam.ipaddress` | One host address, regardless of its NetBox mask. Use a prefix for a network. |
| IP Range | `ipam.iprange` | The range between its start and end addresses. |
| ACL Address Group | `netbox_acls.acladdressgroup` | A reusable collection of address objects. Valid for rule references, not for group membership. |

These are policy conventions for consumers of the data. The plugin does not
perform packet matching or convert address objects into device configuration.

## Families

| ACL family | Allowed rule criteria |
|---|---|
| IPv4 | IPv4 objects and IPv4 address groups. ICMPv4 is allowed, ICMPv6 is not. |
| IPv6 | IPv6 objects and IPv6 address groups. ICMPv6 is allowed, ICMPv4 is not. |
| Dual | IPv4 or IPv6 objects, with one family per rule. |

A group has IPv4 or IPv6 family. There is no Dual group. Its members must match
its family when membership is validated. Objects selected as both source and
destination must still satisfy the rule's family requirements.

An unset address criterion means Any. It supplies no explicit address family
of its own. An empty group remains a reference to that group. It is not the
same value as an unset criterion.

An explicit ICMPv4 or ICMPv6 protocol also contributes a family, even when both
addresses are unset. In a Dual ACL, it must agree with any selected addresses.
In a Dual ACL, a generic ICMP rule with a type needs an address criterion that
determines the family. Otherwise, choose ICMPv4 or ICMPv6. See
[ICMP and TCP flags](../user-guide/protocol-matching.md).

## Identity and related views

References identify objects by their content type and numeric ID. Two IPAM
objects with the same textual address, including objects in different VRFs,
remain different references. The plugin does not add a separate VRF field to
the access list or rule.

Related rule tabs and address filters follow direct references. They do not
evaluate address containment, overlapping networks, or membership through a
group. Group-membership tabs provide the separate link from an IPAM object to
its groups.

## Update and deletion behavior

A reference continues to point to the same object after that object's details
change. Review IPAM changes that affect policy, especially address or family
changes, before using the data for deployment. Membership validation is not a
continuous policy audit.

Referenced IPAM objects and groups are protected from deletion while rules or
group memberships depend on them. Remove the relevant references first.

See [REST API](rest-api.md) for reference payloads and [Bulk operations](../user-guide/bulk-operations.md)
for natural-value and ID imports.
