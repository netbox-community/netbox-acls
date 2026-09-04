import re

import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import netbox_acls.models.mixins
import utilities.json


def validate_address_groups_unused(apps, schema_editor):
    """
    Refuses to reverse while ACL rules still reference an address group.
    """

    db_alias = schema_editor.connection.alias
    ContentType = apps.get_model("contenttypes", "ContentType")
    ACLStandardRule = apps.get_model("netbox_acls", "ACLStandardRule")
    ACLExtendedRule = apps.get_model("netbox_acls", "ACLExtendedRule")

    content_type = ContentType.objects.using(db_alias).filter(app_label="netbox_acls", model="acladdressgroup").first()
    if content_type is None:
        return
    for rule_model, roles in (
        (ACLStandardRule, ("source",)),
        (ACLExtendedRule, ("source", "destination")),
    ):
        for role in roles:
            if rule_model.objects.using(db_alias).filter(**{f"{role}_type_id": content_type.pk}).exists():
                raise RuntimeError(
                    "Cannot remove address groups while ACL rules reference them. "
                    "Remove or replace those rule references before reversing migration 0016."
                )


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0144_customfield_status"),
        ("ipam", "0097_merge_ipaddress_host_index_and_multi_protocol_services"),
        ("netbox_acls", "0015_acl_owner_related_name"),
        ("users", "0016_default_ordering_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aclextendedrule",
            name="destination_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix"))),
                    models.Q(("app_label", "netbox_acls"), ("model", "acladdressgroup")),
                    _connector="OR",
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="aclextendedrule",
            name="source_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix"))),
                    models.Q(("app_label", "netbox_acls"), ("model", "acladdressgroup")),
                    _connector="OR",
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="aclstandardrule",
            name="source_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix"))),
                    models.Q(("app_label", "netbox_acls"), ("model", "acladdressgroup")),
                    _connector="OR",
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.CreateModel(
            name="ACLAddressGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
                ("comments", models.TextField(blank=True)),
                (
                    "name",
                    models.CharField(
                        max_length=500,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[-a-zA-Z0-9_]+\\Z"),
                                "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                                "invalid",
                            )
                        ],
                    ),
                ),
                ("family", models.CharField(db_index=True, default="ipv4", max_length=8)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="users.owner",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "ACL Address Group",
                "verbose_name_plural": "ACL Address Groups",
                "ordering": ("name",),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_destination_acladdressgroup",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_destinations",
                to="netbox_acls.acladdressgroup",
            ),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="_source_acladdressgroup",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="netbox_acls.acladdressgroup",
            ),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="_source_acladdressgroup",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="_%(class)s_sources",
                to="netbox_acls.acladdressgroup",
            ),
        ),
        migrations.CreateModel(
            name="ACLAddressGroupMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("member_id", models.PositiveBigIntegerField()),
                ("comments", models.TextField(blank=True)),
                (
                    "_member_aggregate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_acladdressgroupmembers",
                        to="ipam.aggregate",
                    ),
                ),
                (
                    "_member_ipaddress",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_acladdressgroupmembers",
                        to="ipam.ipaddress",
                    ),
                ),
                (
                    "_member_iprange",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_acladdressgroupmembers",
                        to="ipam.iprange",
                    ),
                ),
                (
                    "_member_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_acladdressgroupmembers",
                        to="ipam.prefix",
                    ),
                ),
                (
                    "address_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="acladdressgroupmembers",
                        to="netbox_acls.acladdressgroup",
                    ),
                ),
                (
                    "member_type",
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix"))
                            )
                        ),
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="users.owner",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "ACL Address Group Member",
                "verbose_name_plural": "ACL Address Group Members",
                "ordering": ("address_group", "member_type", "member_id"),
                "indexes": [models.Index(fields=["member_type", "member_id"], name="netbox_acls_member__0aa6c5_idx")],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("address_group", "member_type", "member_id"),
                        name="netbox_acls_acladdressgroupmember_unique_member",
                        violation_error_message="This object is already a member of the address group.",
                    )
                ],
            },
            bases=(
                netbox_acls.models.mixins.CachedGenericReferenceMixin,
                netbox.models.deletion.DeleteMixin,
                models.Model,
            ),
        ),
        migrations.RunPython(migrations.RunPython.noop, validate_address_groups_unused),
    ]
