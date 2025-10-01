import django.contrib.postgres.fields
import django.contrib.postgres.fields.ranges
from django.db import migrations
from django.db.backends.postgresql.psycopg_any import NumericRange

from netbox_acls.constants import ACL_RULE_PORT_MAX, ACL_RULE_PORT_MIN


def collapse_ints_to_ranges(ints):
    """
    Collapse a list of integers into ranges.

    This function takes a list of integers and converts them into a compact representation
    of ranges. Numbers outside the allowed range (1 to 65,535) are clamped. The integers
    are also sorted, duplicates are removed, and the resulting list is transformed into a
    list of continuous ranges.
    """
    if not ints:
        return []
    # Limit integer to min(1), max(65535), sort, and remove duplicates
    ints = sorted({max(min(int(x), ACL_RULE_PORT_MAX), ACL_RULE_PORT_MIN) for x in ints})
    out = []
    start = prev = ints[0]
    for n in ints[1:]:
        if n == prev + 1:
            prev = n
            continue
        out.append(NumericRange(start, prev + 1))  # store as [start, prev+1) (inclusive human)
        start = prev = n
    out.append(NumericRange(start, prev + 1))  # store as [start, prev+1) (inclusive human)
    return out


def migrate_ports_to_port_ranges(apps, schema_editor):
    """
    Migrates source and destination port values to port range fields in the database.

    This function updates the database by converting individual source and destination
    ports into their respective port ranges for objects in the ACLExtendedRule model.
    If relevant fields (`source_ports` and/or `destination_ports`) are present and contain
    data, this function will compute the corresponding port ranges using the `collapse_ints_to_ranges`
    utility and save the updated data.
    """
    db_alias = schema_editor.connection.alias
    Rule = apps.get_model("netbox_acls", "ACLExtendedRule")
    fields = {f.name for f in Rule._meta.get_fields()}
    has_src_ints = "source_ports" in fields
    has_dst_ints = "destination_ports" in fields

    for r in Rule.objects.using(db_alias).all().iterator():
        changed = False
        if has_src_ints and getattr(r, "source_ports", None) and not getattr(r, "source_port_ranges", None):
            r.source_port_ranges = collapse_ints_to_ranges(r.source_ports)
            changed = True
        if has_dst_ints and getattr(r, "destination_ports", None) and not getattr(r, "destination_port_ranges", None):
            r.destination_port_ranges = collapse_ints_to_ranges(r.destination_ports)
            changed = True
        if changed:
            r.save(update_fields=["source_port_ranges", "destination_port_ranges"])


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0009_accesslist_ip_family"),
    ]

    operations = [
        migrations.AddField(
            model_name="aclextendedrule",
            name="destination_port_ranges",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=django.contrib.postgres.fields.ranges.IntegerRangeField(),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="source_port_ranges",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=django.contrib.postgres.fields.ranges.IntegerRangeField(),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.RunPython(migrate_ports_to_port_ranges, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="aclextendedrule",
            name="destination_ports",
        ),
        migrations.RemoveField(
            model_name="aclextendedrule",
            name="source_ports",
        ),
    ]
