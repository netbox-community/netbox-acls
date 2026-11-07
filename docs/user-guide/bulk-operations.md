# Bulk operations

All plugin object lists support bulk import and bulk edit. Import existing data
or apply the same change to several objects.

## Import data

Select **Import** on the object list and choose CSV, JSON, or YAML.
Create IPAM objects and targets first, then groups, members, ACLs, rules, and
assignments.

Use stored choices such as `extended`, `ipv4`, `permit`, and `tcp`.
Supply every new rule's sequence. Import does not suggest one.

### Access Lists

```csv
name,type,family,default_action,description
WEB-INGRESS,extended,ipv4,deny,Inbound access to web servers
```

### Address groups and members

Import the group first:

```csv
name,family,description
TRUSTED-USERS,ipv4,Networks allowed to reach the service
```

Then import its members from their list at
`/plugins/access-lists/address-groups/members/`, which has no menu entry. This
example requires the prefix to exist:

```csv
address_group,member_type,member
TRUSTED-USERS,ipam.prefix,192.0.2.0/24
```

### Extended Rules

This example requires `WEB-INGRESS`, `TRUSTED-USERS`, and IP address
`198.51.100.10/32` to exist:

```csv
access_list,sequence,action,protocol,source_type,source,destination_type,destination,destination_port_ranges,log_matches,log_options
WEB-INGRESS,10,permit,tcp,netbox_acls.acladdressgroup,TRUSTED-USERS,ipam.ipaddress,198.51.100.10/32,"443,8443",true,syslog
```

Ports use inclusive text ranges: `"443,8000-8080"`. Quote comma-separated cells,
including log options such as `"syslog,cisco-log-input"`. Duplicate/overlapping
ports are rejected. Standard Rules omit destination, protocol, ports, ICMP, and
TCP flag fields.

For ICMP and TCP criteria, use numeric types/codes and lowercase flag values:

```csv
access_list,sequence,action,protocol,icmp_type,icmp_code,tcp_flags,tcp_flags_match
WEB-INGRESS,20,permit,icmpv4,8,0,,
WEB-INGRESS,30,permit,tcp,,,"ack,rst",any
```

ICMP `0` is meaningful, and an empty cell leaves the criterion unrestricted on creation.
A code requires a type. TCP flags are deduplicated and stored in header-bit order.
Use mode `all` or `any`. A blank `tcp_flags_match` defaults to `all` on creation and
preserves the mode on update. See [ICMP and TCP flags](protocol-matching.md).

### Assignments

Use the interface's parent name to distinguish repeated interface names:

```csv
access_list,assigned_object_type,assigned_object,assigned_object_parent,direction
WEB-INGRESS,dcim.interface,eth0,edge-01,ingress
```

The device and interface must already exist. Use `none` for assignments to a
device, virtual chassis, or virtual machine.

## Choose the right object

References accept a natural value or numeric ID, plus an object type such as
`ipam.prefix` or `dcim.interface`.

- Use `source_id`, `destination_id`, `member_id`, or `assigned_object_id` when a
  value is ambiguous. IP ranges always require an ID.
- Provide either a natural value or its ID, not both. An assignment parent
  qualifies a name and cannot be combined with `assigned_object_id`.
- In CSV, use an `access_list.id` or `address_group.id` header to select that
  parent by ID. ACL names may repeat.

JSON/YAML imports use lists of records with plain import field names. Dotted
headers are CSV-specific. Follow the import form's formats. [REST payloads](../reference/rest-api.md)
differ for ports and relationships.

## Update, edit, and export

Include an `id` column to update existing objects. Omitted columns keep their
stored values. To change TCP rule `100` to UDP, explicitly empty its flags:

```csv
id,protocol,tcp_flags
100,udp,
```

Clear incompatible criteria during protocol changes: blank both ICMP cells when
leaving ICMP, and port cells when leaving TCP/UDP. To remove a source, blank
`source_type`, `source`, and `source_id` together. A blank `tcp_flags_match`
preserves its stored value.

For bulk edit, select the objects and choose **Edit**. Blank controls keep their
current values. To remove an ICMP type or code, select its **Set Null** box.

Bulk edit cannot clear port ranges, so clear them through an import update.
**Clear TCP flags** keeps the match mode and cannot be combined with a flag
selection. Setting **Log matches** to **No** clears the log options, while
**Clear log options** keeps the logging setting. Each object must pass
validation.

Use **Export** to download table data. Check import fields before reimporting:
displayed values and related objects may need adjustment.
