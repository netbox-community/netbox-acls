# Access List

An `AccessList` contains Standard or Extended Rules and can be assigned to
several supported targets.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | String | Yes | Up to 500 characters. Letters, numbers, underscores, and hyphens. Not globally unique. |
| `type` | Choice | Yes | `standard` or `extended`. |
| `family` | Choice | Default | `ipv4` by default. Also `ipv6` and `dual`. |
| `default_action` | Choice | Default | `deny` by default. Also `permit` and `reject`. |
| `description` | String | No | Brief description. |
| `owner`, `comments`, `tags`, `custom_fields` | NetBox metadata | No | Standard NetBox ownership and metadata. |

## Relationships and validation

- Standard lists use `aclstandardrules`. Extended lists use `aclextendedrules`.
- `aclassignments` contains the list's assignments.
- Type and family cannot change while any rules exist, including remarks.
- Family changes on an empty list are checked against its existing assignments.
- Renames must preserve host-level name and family uniqueness on assigned targets.

The same name can identify separate lists, so use numeric IDs in integrations
when a name lookup is ambiguous. Names are not automatically case-folded by
the plugin's model validation.

## Lifecycle

Cloning prefills type, family, and default action. It does not duplicate rules
or assignments. Deleting a list deletes its rules and assignments, but keeps
referenced address objects.

## Access

| Surface | Path |
|---|---|
| UI | `/plugins/access-lists/access-lists/` |
| REST | `/api/plugins/access-lists/access-lists/` |

See [Access lists](../../user-guide/access-lists.md), [REST API](../rest-api.md),
and [GraphQL](../graphql.md).
