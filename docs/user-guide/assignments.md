# Assignments

An assignment records where an access list applies. Create one from an object's
**Access Lists** tab, an access list's **Assignments** tab, or
**Access Lists > Assignments**.

## Choose the target

| Target | Direction | Purpose |
|---|---|---|
| Device, Virtual Chassis, Virtual Machine | N/A | Associate a list with the whole object. |
| Interface, VM Interface | Ingress or Egress | Record traffic policy for that interface and direction. |

Host-level and interface assignments are independent. You can assign a list
directly to an interface without first assigning it to the parent. Assigning
it to a parent does not assign it to that parent's interfaces.

## Assign a list

1. Open the target's **Access Lists** tab and select **Assign an ACL**.
2. Choose an existing access list. The target is already selected.
3. For an interface, choose **Ingress** for traffic entering it or **Egress**
   for traffic leaving it.
4. Add comments or ownership information if needed, then save.

Direction is hidden for devices, virtual chassis, and virtual machines.
Those assignments use N/A automatically.

## Interface limits

Each interface and direction can have either:

- One IPv4 list and one IPv6 list, or
- One Dual list, which occupies both address families.

A Dual list therefore conflicts with any other list in the same direction.
Ingress and egress are checked separately. Assignments to different interfaces
are also independent.

## Names on host-level targets

A device, virtual chassis, or virtual machine can have several assigned lists.
Their names must be distinct within each address family on that target. The
same list cannot be assigned to the same target twice.

## Remove an assignment

Delete the assignment to remove the association. The access list and its rules
remain available for other targets. This changes the NetBox record. Apply any
device configuration changes through your usual deployment process.

See [ACL Assignment](../reference/models/aclassignment.md) for exact target
types and validation rules.
