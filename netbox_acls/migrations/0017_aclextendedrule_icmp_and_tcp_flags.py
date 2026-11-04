import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


def validate_icmp_and_tcp_flags_unused(apps, schema_editor):
    """
    Refuses to reverse while ACL rules use ICMP or TCP flag criteria.
    """

    db_alias = schema_editor.connection.alias
    ACLExtendedRule = apps.get_model("netbox_acls", "ACLExtendedRule")

    criteria = (
        models.Q(protocol__in=("icmpv4", "icmpv6"))
        | models.Q(icmp_type__isnull=False)
        | models.Q(icmp_code__isnull=False)
        | ~models.Q(tcp_flags=[])
    )
    if ACLExtendedRule.objects.using(db_alias).filter(criteria).exists():
        raise RuntimeError(
            "Cannot remove ICMP and TCP flag criteria while ACL rules use them. "
            "Clear ICMP types, codes and TCP flags and replace the icmpv4 and icmpv6 protocols "
            "before reversing migration 0017."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0016_acl_address_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="aclextendedrule",
            name="icmp_code",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)]
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="icmp_type",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)]
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="tcp_flags",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=30), blank=True, default=list
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="tcp_flags_match",
            field=models.CharField(default="all", max_length=30),
        ),
        migrations.RunPython(migrations.RunPython.noop, validate_icmp_and_tcp_flags_unused),
    ]
