# GraphQL

Use NetBox's read-only GraphQL API at `/graphql/` to retrieve ACLs and related
objects in one query. It uses the same authentication and object permissions as
the [REST API](rest-api.md). Use REST for changes.

## Query fields

| Object | Single object | List |
| --- | --- | --- |
| Access List | `access_list` | `access_list_list` |
| Standard Rule | `acl_standard_rule` | `acl_standard_rule_list` |
| Extended Rule | `acl_extended_rule` | `acl_extended_rule_list` |
| Assignment | `acl_assignment` | `acl_assignment_list` |
| Address Group | `acl_address_group` | `acl_address_group_list` |
| Address Group Member | `acl_address_group_member` | `acl_address_group_member_list` |

Single-object queries take an `id`, for example `access_list(id: 10)`.
List queries accept `filters`. Choice filters use uppercase enum values such as
`EXTENDED`, `IPV4`, `PERMIT`, and `TCP`. REST writes use lowercase strings.

## Retrieve an ACL with its rules

```graphql
query {
  access_list_list(filters: {name: {exact: "WEB-INGRESS"}, type: {exact: EXTENDED}}) {
    id
    name
    family
    default_action
    aclextendedrules {
      sequence
      action
      protocol
      source {
        __typename
        ... on ACLAddressGroupType {
          id
          name
        }
        ... on PrefixType {
          id
          prefix
        }
      }
      destination_port_ranges
      icmp_type
      icmp_code
      tcp_flags
      tcp_flags_match
      log_matches
      log_options
    }
  }
}
```

Use `aclstandardrules` for a Standard ACL and `aclassignments` for its assignments.
Source, destination, member, and assigned-object fields can return different
object types. Use `__typename` and inline fragments to select their fields.

Port ranges are exposed as strings. A stored range such as `"[443, 444)"`
includes 443 and excludes 444. The REST API represents the same single port as
`[[443, 443]]`.

## Filter protocol criteria

ICMP type/code fields return integers or `null`. TCP flags return lowercase
strings. Use these list-filter inputs:

| Criterion | Filter input |
| --- | --- |
| Explicit ICMPv6 protocol | `protocol: {exact: ICMPV6}` |
| ICMP type 0 | `icmp_type: {filter_lookup: {exact: 0}}` |
| ICMP code 0 | `icmp_code: {filter_lookup: {exact: 0}}` |
| A selected ACK or RST flag | `tcp_flags: {overlap: ["ack", "rst"]}` |
| Any flag match mode | `tcp_flags_match: {exact: ANY}` |

The corresponding protocol enum for ICMPv4 is `ICMPV4`. Generic `ICMP` remains
separate. Combine numeric ICMP criteria with the relevant protocol and ACL context.
`tcp_flags` searches stored selections. Its filter is independent of the rule's
`all` or `any` match mode, which is ignored for packet criteria when no flags are
selected. See [ICMP and TCP flags](../user-guide/protocol-matching.md).

## Follow address group membership

Replace `20` with an existing group ID:

```graphql
query {
  acl_address_group(id: 20) {
    name
    family
    acladdressgroupmembers {
      id
      member {
        __typename
        ... on PrefixType {
          id
          prefix
        }
        ... on IPAddressType {
          id
          address
        }
      }
    }
  }
}
```

Groups also expose `accesslist_standard_rule_sources`,
`accesslist_extended_rule_sources`, and `accesslist_extended_rule_destinations`
for rules that reference the group itself.

## Start from a NetBox object

Devices, interfaces, virtual chassis, virtual machines, and VM interfaces expose
`acl_assignments`. Aggregates, prefixes, IP addresses, and IP ranges expose:

- `acl_standard_rule_sources`
- `acl_extended_rule_sources`
- `acl_extended_rule_destinations`
- `acl_address_group_members`

These are direct relationships. A prefix inside an address group does not list
rules referencing that group as direct prefix references. Follow its memberships
to the group to inspect those rules.

Filter logging with `log_matches: {exact: true}` or
`log_options: {overlap: ["syslog"]}`. Use the schema browser for the complete
filter options. Keep queries focused with filters and request only the fields
and relationships needed by your integration.
