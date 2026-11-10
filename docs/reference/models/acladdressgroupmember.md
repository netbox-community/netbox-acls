# ACL Address Group Member

An `ACLAddressGroupMember` records one IPAM object's membership in an address
group. It references that object rather than copying its address data.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `address_group` | ACL Address Group | Yes | Existing group. |
| `member_type` | Content type | Yes | `ipam.aggregate`, `ipam.prefix`, `ipam.ipaddress`, or `ipam.iprange`. |
| `member_id` | Integer | Yes | Positive ID of an existing object of that type. |
| `owner`, `comments`, `tags`, `custom_fields` | NetBox metadata | No | Metadata for the membership itself. |

The UI combines `member_type` and `member_id` into a **Member** selector.

## Validation

The member must match the group's family. The combination of group, content
type, and object ID must be unique. An object can belong to several groups.
Different objects with overlapping addresses remain separate memberships.

A membership cannot refer to another group. It has no sequence, action,
protocol, or ports.

## Lifecycle

Deleting a membership removes that association and keeps the IPAM object.
Deleting the group removes its memberships. An IPAM object cannot be deleted
while a membership references it.

Cloning retains the group and leaves the member selection empty, so the new
record does not immediately duplicate the existing membership.

## Access

| Surface | Path |
|---|---|
| UI | `/plugins/access-lists/address-groups/members/` |
| REST | `/api/plugins/access-lists/address-group-members/` |

Use the group's **Members** panel for normal editing. The membership list and
its Import action are available at the UI path above. Members do not have a
separate top-level navigation entry.

See [Address groups](../../user-guide/address-groups.md), [Bulk operations](../../user-guide/bulk-operations.md),
and [REST API](../rest-api.md).
