# Configuration

NetBox ACLs works with its defaults. Add optional settings under
`PLUGINS_CONFIG["netbox_acls"]` in NetBox's configuration, keeping any existing
plugin entries:

```python
PLUGINS_CONFIG = {
    "netbox_acls": {
        "top_level_menu": True,
        "rule_sequence_step": 10,
    },
}
```

Restart the NetBox processes after changing configuration.

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `top_level_menu` | `True` | Show a separate **Access Lists** menu. Set to `False` to place its entries under **Plugins**. |
| `rule_sequence_step` | `10` | Increment used when suggesting a sequence number for a new or cloned rule. |

Use a positive integer for `rule_sequence_step`. With the default, an empty
access list starts at `10`, and a list whose highest sequence is `30` receives a
suggestion of `40`.

## Sequence suggestions

The add form suggests a sequence when opened with an access list already
selected. Cloning a rule also calculates the next sequence. You can enter a
different available number to insert a rule between existing entries.

Changing the step does not renumber existing rules. It also does not allocate
sequence numbers for REST requests or bulk imports: those callers must provide
the required value. Two people adding rules at the same time can receive the
same suggestion, and the duplicate must be corrected before saving.

Menu placement does not grant access. Use NetBox's object permissions to control
which entries and objects a user can see. See [Permissions](permissions.md).

## Customized protocol choices

Extend the protocol choices through NetBox's `FIELD_CHOICES` setting to document
a protocol the plugin does not ship. [Field choices](../reference/choices.md#protocol)
lists the built-in values.

```python
FIELD_CHOICES = {
    "netbox_acls.ACLExtendedRule.protocol+": [
        ("esp", "ESP"),
        ("vrrp", "VRRP"),
    ],
}
```

The trailing `+` appends to the built-in values. Without it, the configured list
replaces them, so include every value your rules already use. A replacement key
takes precedence when both are configured. Appended values render after the
built-in groups, and a stored value may be at most 30 characters. To show a
description in the forms, give a value as a dictionary, for example
`{"value": "esp", "label": "ESP", "description": "Encapsulating Security Payload"}`.

Changing choices does not extend protocol-specific validation. Ports still
require TCP or UDP, TCP flags require TCP, and ICMP types require an ICMP
protocol. Your automation must handle any value you add. Restart NetBox after
updating these settings.

!!! note "Upgrading to 2.2.0"

    2.2.0 adds the explicit `icmpv4` and `icmpv6` protocols. A replacement list
    without them cannot offer them, so add both. An extension that already added
    its own `icmpv4` or `icmpv6` lists that value twice, and its color overrides
    the built-in one. Rules stored with such a value gain the family check on
    their next edit and block reversing migration `0017`.

### Log options

The key `netbox_acls.ACLRule.log_options` covers the log options of both rule
types. [Field choices](../reference/choices.md#log-options) lists the built-in
values and their groups.

```python
FIELD_CHOICES = {
    "netbox_acls.ACLRule.log_options+": [
        ("vendor-x-include-zone", "Include security zone (Vendor X)"),
    ],
}
```

The `+` suffix, replacement, and dictionary form work as for protocols, and a
stored value may be at most 100 characters. Prefix an added value with its
vendor, as `cisco-log-input` does, and name the vendor in its label. The REST
API, GraphQL, and the database carry the value, and the forms and table exports
show the label. Your automation must handle any value you add.
