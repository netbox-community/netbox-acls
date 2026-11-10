# ACL Address Group

An `ACLAddressGroup` is a named collection of IPAM objects that rules can
reference as a source or destination.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | String | Yes | Globally unique, up to 500 characters. Letters, numbers, underscores, and hyphens. |
| `family` | Choice | Default | `ipv4` by default, or `ipv6`. Dual is not supported. |
| `description` | String | No | Brief description. |
| `owner`, `comments`, `tags`, `custom_fields` | NetBox metadata | No | Standard ownership and metadata. |

## Relationships

`acladdressgroupmembers` holds the membership records. A group can be the source
of a Standard Rule, or the source or destination of an Extended Rule. The same
group can be reused in several access lists.

Members may be aggregates, prefixes, IP addresses, or IP ranges. Nested groups,
service groups, and protocol groups are not supported.

## Validation and lifecycle

- All members must have the group's family.
- The family cannot change while the group has members or any rule references.
- Empty groups are allowed, including groups referenced by rules. Consumers
  must define their empty-group handling. An empty group is not an unset criterion.
- Deletion is blocked while rules reference the group.
- Deleting an unused group deletes membership records and preserves IPAM objects.
- Cloning prefills the family. It does not copy the name or members.

Membership and rule rows are restricted by your permissions. Tab badges and
group member counts can include objects you cannot view.

## Access

| Surface | Path |
|---|---|
| UI | `/plugins/access-lists/address-groups/` |
| REST | `/api/plugins/access-lists/address-groups/` |

See [Address groups](../../user-guide/address-groups.md) and [Address references](../addressing.md).
