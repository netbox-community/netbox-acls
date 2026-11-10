# NetBox ACLs

Document access control lists, their rules, and where they apply in NetBox.

NetBox ACLs gives network teams a shared, vendor-neutral record of intended
traffic policy. Reuse NetBox IPAM objects and address groups in your rules,
then assign an access list to a device, virtual chassis, virtual machine,
or interface.

## Getting started

| What you need to do | Start here |
|---|---|
| Document your first ACL | [Getting started](user-guide/getting-started.md) |
| Add or change traffic rules | [Rules](user-guide/rules.md) |
| Match ICMP messages or TCP flags | [ICMP and TCP flags](user-guide/protocol-matching.md) |
| Reuse a set of addresses | [Address groups](user-guide/address-groups.md) |
| Associate an ACL with a device or interface | [Assignments](user-guide/assignments.md) |
| Install or operate the plugin | [Installation](administration/installation.md), [Configuration](administration/configuration.md), and [Permissions](administration/permissions.md) |
| Integrate with automation | [REST API](reference/rest-api.md) and [GraphQL](reference/graphql.md) |
| Contribute a change | [Contributing](development/contributing.md) |

## Main concepts

| Term | Meaning |
|---|---|
| Access list | A named, ordered collection of Standard or Extended Rules, with an address family and default action. |
| Rule | A permit, deny, or remark entry at a sequence number within an access list. |
| Address group | A reusable collection of IPv4 or IPv6 objects from NetBox IPAM. |
| Assignment | An association between an access list and a device, virtual chassis, virtual machine, or interface. |

The plugin records policy. Configuration generation, deployment, traffic
enforcement, and packet evaluation belong to your network automation and devices.
