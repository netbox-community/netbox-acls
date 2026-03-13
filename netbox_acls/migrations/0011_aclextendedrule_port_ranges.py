import django.contrib.postgres.fields
import django.contrib.postgres.fields.ranges
from django.db import migrations
from django.db.models import Q
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
        out.append(NumericRange(start, prev + 1))  # store as [start, prev+1) (inclusive)
        start = prev = n
    out.append(NumericRange(start, prev + 1))  # store as [start, prev+1) (inclusive)
    return out


def migrate_ports_to_port_ranges(apps, schema_editor):
    """
    Migrates source and destination port values to port range fields in the database.
    """
    db_alias = schema_editor.connection.alias
    Rule = apps.get_model("netbox_acls", "ACLExtendedRule")
    fields = {f.name for f in Rule._meta.get_fields()}
    has_src_ints = "source_ports" in fields
    has_dst_ints = "destination_ports" in fields

    if not has_src_ints and not has_dst_ints:
        return

    # Only fetch rows where ports exist
    filters = Q()
    if has_src_ints:
        filters |= Q(source_ports__isnull=False)
    if has_dst_ints:
        filters |= Q(destination_ports__isnull=False)

    rules_to_update = []
    for r in Rule.objects.using(db_alias).filter(filters).iterator():
        if has_src_ints and r.source_ports:
            r.source_port_ranges = collapse_ints_to_ranges(r.source_ports)
        if has_dst_ints and r.destination_ports:
            r.destination_port_ranges = collapse_ints_to_ranges(r.destination_ports)
        rules_to_update.append(r)

    Rule.objects.using(db_alias).bulk_update(
        rules_to_update, ["source_port_ranges", "destination_port_ranges"], batch_size=100
    )


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0010_accesslist_ip_family"),
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
