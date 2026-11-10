# ACL Assignment

An `ACLAssignment` connects one access list to one supported target.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `access_list` | Access List | Yes | Existing list. Use its ID in REST writes. |
| `assigned_object_type` | Content type | Yes | One of the types below. |
| `assigned_object_id` | Integer | Yes | ID of the target object. |
| `direction` | Choice | Yes in API/import payloads | `ingress`, `egress`, or `none`. Host targets are normalized to `none`. |
| `family` | Choice | Read-only | Copied from the access list. |
| `owner`, `comments`, `tags`, `custom_fields` | NetBox metadata | No | Metadata for the assignment itself. |

The UI represents the content type and ID through a single object selector.

## Targets

| Content type | Direction |
|---|---|
| `dcim.device` | `none` |
| `dcim.virtualchassis` | `none` |
| `virtualization.virtualmachine` | `none` |
| `dcim.interface` | `ingress` or `egress` |
| `virtualization.vminterface` | `ingress` or `egress` |

## Validation

On an interface, each direction permits one IPv4 and one IPv6 assignment,
or one Dual assignment. Dual conflicts with either single family.

On a device, virtual chassis, or virtual machine, the combination of ACL name
and exact family must be unique. A duplicate assignment of the same ACL,
target, and direction is rejected.

A parent assignment is not required for an interface assignment. Assignments
do not propagate to interfaces, virtual chassis members, or other objects.

Deleting an assignment keeps its ACL and rules. Deleting the access list also
removes its assignments.

## Access

| Surface | Path |
|---|---|
| UI | `/plugins/access-lists/assignments/` |
| REST | `/api/plugins/access-lists/assignments/` |

See [Assignments](../../user-guide/assignments.md) and [REST API](../rest-api.md).
