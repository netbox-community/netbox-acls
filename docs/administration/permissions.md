# Permissions

Grant access through NetBox's **Object Permissions**, preferably to groups that
match your team's responsibilities. Each ACL object type has its own `view`,
`add`, `change`, and `delete` actions.

## Object types

| Object type | Permission model name |
|---|---|
| Access List | `accesslist` |
| ACL Standard Rule | `aclstandardrule` |
| ACL Extended Rule | `aclextendedrule` |
| ACL Assignment | `aclassignment` |
| ACL Address Group | `acladdressgroup` |
| ACL Address Group Member | `acladdressgroupmember` |

The namespace is `netbox_acls`. For example,
`netbox_acls.view_accesslist` allows viewing access lists within the permission's
constraints. ICMP and TCP flag criteria are fields of ACL Extended Rules and need
no permission of their own.

## Suggested roles

| Role | Permissions to consider |
|---|---|
| Reader | `view` on the ACL object types they need, plus relevant IPAM and device or virtualization objects. |
| Rule editor | Reader access and `add` / `change` on the applicable rule types. Grant `delete` separately if required. |
| Group maintainer | Reader access and the necessary write actions on both Address Groups and Address Group Members. |
| Assignment editor | Reader access and the necessary write actions on ACL Assignments. |

Access to an access list does not replace permissions on its rules or
assignments. Likewise, editing a group and editing its membership are separate
actions. Grant view access to referenced objects so users can find them in
selectors and follow their links.

## Related tabs and API access

The **Access Lists** tab on devices and interfaces requires assignment view
permission. Rule-reference tabs on IPAM objects and address groups require the
corresponding rule view permission. The **ACL Address Groups** tab requires
member view permission. Some reference tabs are also hidden when empty. A tab's
badge counts every related object, including objects the user cannot view.

REST and GraphQL use the authenticated user's NetBox permissions. Review
automation accounts as carefully as interactive accounts, and test constrained
roles with representative objects. See [REST API](../reference/rest-api.md).
