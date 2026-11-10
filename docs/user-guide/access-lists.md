# Access lists

An access list holds ordered rules and records the action to take when no rule
matches. Create the list before adding rules or assignments.

## Choose a type and family

| Choice | Use it for |
|---|---|
| Standard | Policy based on the source address. |
| Extended | Policy that also uses destination addresses, protocols, or TCP/UDP ports. |
| IPv4 | Rules with IPv4 address criteria. |
| IPv6 | Rules with IPv6 address criteria. |
| Dual | A list containing IPv4 rules and IPv6 rules. A single rule must not mix the two families. |

The form shows a short description beside each choice. The type and family
cannot change while the list contains rules. Create a new
list when you need a different policy structure.

## Create and maintain a list

1. Open **Access Lists > Access Lists** and select **Add**.
2. Enter a name using letters, numbers, underscores, or hyphens.
3. Select its type, family, and default action.
4. Add a description, owner, or tags if useful to your team, then save.
5. Use **Add Rule** to build the policy and the **Assignments** tab to record
   where it applies.

Names can be reused for separate access lists. On a particular device, virtual
chassis, or virtual machine, however, two assigned lists cannot have the same
name and family. Use IDs when an import or integration must distinguish lists
with the same name.

## Default action

| Action | Intended policy |
|---|---|
| Deny | Drop traffic that does not match a rule. This is the default. |
| Permit | Allow traffic that does not match a rule. |
| Reject (Reset) | Record an explicit rejection policy. Its translation depends on the target platform. |

The default action belongs to the access list. Individual rules support Permit,
Deny, and Remark.

## Copying and deleting

Cloning a list prefills its type, family, and default action for a new list.
It does not copy its rules or assignments.

Deleting a list also deletes its rules and assignments. Referenced IPAM objects
and address groups remain. Review the deletion confirmation before proceeding.

See the [Access List reference](../reference/models/accesslist.md) for field
details and update restrictions.
