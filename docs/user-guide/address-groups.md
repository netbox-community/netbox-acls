# Address groups

Use an address group when several rules share the same set of addresses.
The rules reference the group, so you can maintain its membership in one place.

## Create a group

1. Open **Access Lists > Address Groups** and select **Add**.
2. Enter a unique name, such as `Monitoring_Servers`.
3. Choose **IPv4** or **IPv6**, then save.
4. In the **Members** panel, select **Add Member**.
5. Select an existing aggregate, prefix, IP address, or IP range, then save.
   Repeat for the other members.

All members must have the group's family. The same NetBox object can appear
only once in a group, but it may belong to several groups. A group can contain
different kinds of IPAM object.

## Use the group in a rule

Select **ACL Address Group** as the source or destination object type, then
choose the group. Standard Rules support groups as sources, and Extended Rules
support them as sources and destinations.

For example, an IPv4 group named `Monitoring_Servers` can contain the hosts
`192.0.2.10/32` and `192.0.2.11/32`. Reference that group in rules that permit
the monitoring traffic your team needs.

## Review where a group is used

When rules reference the group, its **ACL Standard Rules** and **ACL Extended
Rules** tabs list them. Extended Rules identify source, destination, or both.
An IPAM object in a group shows its memberships on an **ACL Address Groups** tab.

IPAM rule tabs show direct references only. To find rules that use an object
through a group, open its **ACL Address Groups** tab, then the group's rule
tabs. These views do not expand prefixes or search for overlapping addresses.

## Maintain membership carefully

Changing membership affects the policy represented by every rule using that
group. Review those rules before making the change.

- A group can be empty while you prepare it. An empty group is not an **Any**
  address selector. Decide how your automation handles it before deployment.
- You cannot change its family while it has members or is referenced by rules.
- You cannot delete a referenced group. Remove or change its rule references first.
- Deleting an unused group removes its memberships and keeps the IPAM objects.
- Cloning a group does not copy its members.

Groups cannot contain other groups, services, or protocols.
