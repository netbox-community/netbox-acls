# ACL Standard Rule

An `ACLStandardRule` documents a source-based permit or deny entry, or a
standalone remark, in a Standard access list.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `access_list` | Access List | Yes | Must have type `standard`. |
| `sequence` | Integer | Yes | Non-negative, unique within the list. Determines order. |
| `action` | Choice | Yes | `permit`, `deny`, or `remark`. |
| `remark` | String | For Remark | Up to 500 characters. May also annotate Permit or Deny. |
| `source_type`, `source_id` | Content type and ID | No | Reference an address object or group. Both unset means Any. |
| `log_matches` | Boolean | Default | `false`. Records logging intent. |
| `log_options` | List of choices | No | Empty by default. Requires `log_matches=true`. |
| `description` | String | No | Up to 500 characters. |
| `owner`, `comments`, `tags`, `custom_fields` | NetBox metadata | No | Standard ownership and metadata. |

## Validation

The source must satisfy the ACL's [address family](../addressing.md). A Remark
requires text and cannot have a source, logging enabled, or log options.
Remarks use their own sequence number.

Log options are deduplicated and sorted. The built-in choices are `syslog`
and `cisco-log-input`. These values describe a device configuration request.
The plugin does not produce packet logs.

## Lifecycle

The UI can suggest a sequence when the parent ACL is known. REST and imports
require it explicitly. Cloning a rule suggests the next sequence and carries
its configured traffic and logging fields into the creation form. Review the
new form before saving.

Deleting the ACL deletes the rule. Deleting the rule leaves its referenced
IPAM object or group intact.

## Access

| Surface | Path |
|---|---|
| UI | `/plugins/access-lists/standard-rules/` |
| REST | `/api/plugins/access-lists/standard-acl-rules/` |

See [Rules](../../user-guide/rules.md) and [REST API](../rest-api.md).
