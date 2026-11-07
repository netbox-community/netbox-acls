# Field choices

Use the stored values below in REST writes and bulk imports. Create, edit, and
bulk-edit forms show each label with its description, and filter forms show the
label only. [GraphQL](graphql.md) filters use generated enum values, such as
`EXTENDED` for `extended`.

## Access lists

### Type

| Value | Label | Description |
|---|---|---|
| `extended` | Extended | Matches source, destination and protocol criteria |
| `standard` | Standard | Matches the source only |

### Family

| Value | Label | Description |
|---|---|---|
| `ipv4` | IPv4 | IPv4 addresses only |
| `ipv6` | IPv6 | IPv6 addresses only |
| `dual` | Dual | IPv4 and IPv6 addresses |

### Default action

| Value | Label | Description |
|---|---|---|
| `deny` | Deny | Drop the traffic |
| `permit` | Permit | Allow the traffic |
| `reject` | Reject (Reset) | Drop the traffic and notify the sender |

`reject` is an access list default action, not a rule action.

## Address groups

### Family

| Value | Label | Description |
|---|---|---|
| `ipv4` | IPv4 | IPv4 addresses only |
| `ipv6` | IPv6 | IPv6 addresses only |

An address group has no Dual family.

## Rules

### Action

| Value | Label | Description |
|---|---|---|
| `deny` | Deny | Drop the traffic |
| `permit` | Permit | Allow the traffic |
| `remark` | Remark | A comment with no match criteria |

### Protocol

Extended Rules only. The forms group the values as **Common** and **Routing and
tunneling**. A blank protocol is stored as unspecified, and port ranges require
`tcp` or `udp`.

| Value | Label | Description |
|---|---|---|
| `icmp` | ICMP | Follows the ACL or address family |
| `icmpv4` | ICMPv4 | Always IPv4, IP protocol 1 |
| `icmpv6` | ICMPv6 | Always IPv6, IP protocol 58 |
| `ip` | IP | Any IP protocol |
| `tcp` | TCP | Transmission Control Protocol, IP protocol 6 |
| `udp` | UDP | User Datagram Protocol, IP protocol 17 |
| `gre` | GRE | Generic Routing Encapsulation, IP protocol 47 |
| `eigrp` | EIGRP | Enhanced Interior Gateway Routing Protocol, IP protocol 88 |
| `ospf` | OSPF | Open Shortest Path First, IP protocol 89 |
| `pim` | PIM | Protocol Independent Multicast, IP protocol 103 |

### TCP flags

Extended Rules with protocol `tcp` only. Duplicates are removed, and flags are
stored in the order of this table.

| Value | Label | Description |
|---|---|---|
| `fin` | FIN | No more data from the sender |
| `syn` | SYN | Synchronize sequence numbers |
| `rst` | RST | Reset the connection |
| `psh` | PSH | Push buffered data to the application |
| `ack` | ACK | Acknowledgment field is significant |
| `urg` | URG | Urgent pointer field is significant |
| `ece` | ECE | ECN-Echo |
| `cwr` | CWR | Congestion window reduced |
| `ae` | AE | Accurate ECN, formerly NS |

### TCP flag match mode

`all` is the default. With no flags selected, the mode has no effect.

| Value | Label | Description |
|---|---|---|
| `all` | All | Every selected flag is set |
| `any` | Any | At least one selected flag is set |

### Log options

The forms group the values as **Generic** and **Cisco**. `log_options` requires
`log_matches=true`, and the stored options are deduplicated and sorted.

| Value | Label | Description |
|---|---|---|
| `syslog` | Syslog | Send log messages to syslog |
| `cisco-log-input` | Log-input | Include the input interface and source MAC address when available |

## ICMP criteria

`icmp_type` and `icmp_code` accept integers from `0` to `255`, or `null` for no
restriction. A code requires a type. These are numeric fields rather than fixed
choices, and the form's type presets do not limit the accepted values. Generic
`icmp` follows the ACL or address family. `icmpv4` and `icmpv6` select it
explicitly and must agree with the ACL and address criteria. See
[ICMP and TCP flags](../user-guide/protocol-matching.md) for examples and the
stateless ACK and RST pattern.

## Assignments

### Direction

| Value | Label |
|---|---|
| `ingress` | Ingress |
| `egress` | Egress |
| `none` | N/A |

`ingress` and `egress` apply to interfaces and VM interfaces. `none` applies to
devices, virtual chassis, and virtual machines. An assignment's family follows
its access list and is read-only in the REST API.

## Custom choices

The protocol and log option choices can be extended through NetBox's
`FIELD_CHOICES`. Adding a value does not add validation, device support, or
protocol-specific fields. See
[Customized protocol choices](../administration/configuration.md#customized-protocol-choices).
