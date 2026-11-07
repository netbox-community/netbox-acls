# Getting started

This example documents HTTPS access from a user network to one server.
The addresses are examples. Use the objects that represent your own network.

## Before you start

Ask your administrator for permission to view and create ACLs, rules, and
assignments, and to view the IPAM and interface objects you will select.
Ensure these objects already exist in NetBox:

| Object | Example |
|---|---|
| Source prefix | `192.0.2.0/24` |
| Destination IP address | `198.51.100.10/32` |
| Assignment target | An existing device interface |

## 1. Create the access list

Open **Access Lists > Access Lists** and select **Add**. If the plugin uses the
Plugins menu, open its Access Lists entry there instead.

| Field | Value |
|---|---|
| Name | `Users_HTTPS` |
| Type | Extended |
| Family | IPv4 |
| Default action | Deny |

Save the access list. Choose Extended because this example needs a destination,
a protocol, and a port.

## 2. Add the rule

On the access list, select **Add Rule** and enter:

| Field | Value |
|---|---|
| Sequence | `10` |
| Action | Permit |
| Protocol | TCP |
| Source | The prefix `192.0.2.0/24` |
| Destination | The IP address `198.51.100.10/32` |
| Destination Port Ranges | `443` |

Leave source ports empty to document any source port. Add a short description,
then save. The list now records one permitted flow and a default deny action.

## 3. Add an assignment

Open the interface's **Access Lists** tab and select **Assign an ACL**. Choose
`Users_HTTPS` and the direction that matches your intended policy:

- **Ingress:** traffic entering the interface.
- **Egress:** traffic leaving the interface.

Save the assignment. Review the access list's rules and **Assignments** tab
before using the data in your configuration workflow.

Saving these objects updates NetBox. Your deployment process is responsible
for applying the policy to the network.

## Next steps

Use [Address groups](address-groups.md) to reuse several addresses, or
[Bulk operations](bulk-operations.md) to import larger policies.
