import re

import django.contrib.postgres.fields
import django.contrib.postgres.fields.ranges
import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):
    replaces = [
        ("netbox_acls", "0001_initial"),
        ("netbox_acls", "0002_alter_accesslist_options_and_more"),
        ("netbox_acls", "0003_netbox_acls"),
        ("netbox_acls", "0004_netbox_acls"),
        ("netbox_acls", "0005_preflight_validate_upgrade"),
        ("netbox_acls", "0006_alter_accesslist_name"),
        ("netbox_acls", "0007_acl_rule_sequence_unique"),
        ("netbox_acls", "0008_acl_assignments"),
        ("netbox_acls", "0009_accesslist_ip_family"),
        ("netbox_acls", "0010_acl_rule_source_and_destination_objects"),
        ("netbox_acls", "0011_acl_rule_copy_prefix_assignments"),
        ("netbox_acls", "0012_aclextendedrule_port_ranges"),
        ("netbox_acls", "0013_acl_owner"),
    ]

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0072_created_datetimefield"),
        ("extras", "0128_tableconfig"),
        ("ipam", "0081_remove_service_device_virtual_machine_add_parent_gfk_index"),
        ("users", "0015_owner"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessList",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=500,
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[-a-zA-Z0-9_]+\\Z"),
                                "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                                "invalid",
                            )
                        ],
                    ),
                ),
                ("type", models.CharField(max_length=30)),
                ("default_action", models.CharField(default="deny", max_length=30)),
                ("comments", models.TextField(blank=True)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                ("family", models.CharField(db_index=True, default="ipv4", max_length=8)),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Access List",
                "verbose_name_plural": "Access Lists",
            },
        ),
        migrations.CreateModel(
            name="ACLAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                (
                    "access_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aclassignments",
                        to="netbox_acls.accesslist",
                    ),
                ),
                ("direction", models.CharField(max_length=30)),
                ("assigned_object_id", models.PositiveBigIntegerField()),
                (
                    "assigned_object_type",
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(
                                    ("app_label", "dcim"), ("model__in", ("device", "interface", "virtualchassis"))
                                ),
                                models.Q(
                                    ("app_label", "virtualization"), ("model__in", ("virtualmachine", "vminterface"))
                                ),
                                _connector="OR",
                            )
                        ),
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.contenttype",
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                ("family", models.CharField(db_index=True, editable=False, max_length=8)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
                    ),
                ),
            ],
            options={
                "ordering": ["assigned_object_type", "assigned_object_id", "access_list", "family", "direction"],
                "unique_together": set(),
                "verbose_name": "ACL Interface Assignment",
                "verbose_name_plural": "ACL Interface Assignments",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("access_list", "assigned_object_type", "assigned_object_id", "direction"),
                        name="netbox_acls_aclassignment_unique_object_direction_family_per_access_list",
                        violation_error_message="ACL Assignment for the given object and direction.",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("direction", "none"), _negated=True),
                        fields=("assigned_object_type", "assigned_object_id", "direction", "family"),
                        name="netbox_acls_aclassignment_unique_object_direction_family_interface_only",
                        violation_error_message="ACL Assignment for the given object, direction and family exists.",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="ACLExtendedRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "access_list",
                    models.ForeignKey(
                        limit_choices_to={"type": "extended"},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aclextendedrules",
                        to="netbox_acls.accesslist",
                    ),
                ),
                ("sequence", models.PositiveIntegerField()),
                ("description", models.CharField(blank=True, max_length=500)),
                ("action", models.CharField(max_length=30)),
                ("remark", models.CharField(blank=True, max_length=500)),
                (
                    "_source_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.prefix",
                    ),
                ),
                (
                    "_destination_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_destinations",
                        to="ipam.prefix",
                    ),
                ),
                ("protocol", models.CharField(blank=True, max_length=30)),
                (
                    "_destination_aggregate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_destinations",
                        to="ipam.aggregate",
                    ),
                ),
                (
                    "_destination_ipaddress",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_destinations",
                        to="ipam.ipaddress",
                    ),
                ),
                (
                    "_destination_iprange",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_destinations",
                        to="ipam.iprange",
                    ),
                ),
                (
                    "_source_aggregate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.aggregate",
                    ),
                ),
                (
                    "_source_ipaddress",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.ipaddress",
                    ),
                ),
                (
                    "_source_iprange",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.iprange",
                    ),
                ),
                ("destination_id", models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    "destination_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix"))
                            )
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                ("source_id", models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    "source_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix"))
                            )
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "destination_port_ranges",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.ranges.IntegerRangeField(),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "source_port_ranges",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.ranges.IntegerRangeField(),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
                    ),
                ),
            ],
            options={
                "ordering": ("access_list", "sequence", "-action"),
                "verbose_name": "ACL Extended Rule",
                "verbose_name_plural": "ACL Extended Rules",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("access_list", "sequence"),
                        name="netbox_acls_aclextendedrule_unique_aclrule_sequence",
                        violation_error_message="Unique ACL rule sequence already exists.",
                    )
                ],
                "indexes": [
                    models.Index(
                        fields=["destination_type", "destination_id", "source_type", "source_id"],
                        name="netbox_acls_destina_8f93b4_idx",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="ACLStandardRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "access_list",
                    models.ForeignKey(
                        limit_choices_to={"type": "standard"},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aclstandardrules",
                        to="netbox_acls.accesslist",
                    ),
                ),
                ("sequence", models.PositiveIntegerField()),
                ("description", models.CharField(blank=True, max_length=500)),
                ("action", models.CharField(max_length=30)),
                ("remark", models.CharField(blank=True, max_length=500)),
                (
                    "_source_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.prefix",
                    ),
                ),
                (
                    "_source_aggregate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.aggregate",
                    ),
                ),
                (
                    "_source_ipaddress",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.ipaddress",
                    ),
                ),
                (
                    "_source_iprange",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="_%(class)s_sources",
                        to="ipam.iprange",
                    ),
                ),
                ("source_id", models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    "source_type",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "ipam"), ("model__in", ("aggregate", "ipaddress", "iprange", "prefix"))
                            )
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="users.owner"
                    ),
                ),
            ],
            options={
                "ordering": ("access_list", "sequence", "-action"),
                "unique_together": set(),
                "verbose_name": "ACL Standard Rule",
                "verbose_name_plural": "ACL Standard Rules",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("access_list", "sequence"),
                        name="netbox_acls_aclstandardrule_unique_aclrule_sequence",
                        violation_error_message="Unique ACL rule sequence already exists.",
                    )
                ],
                "indexes": [models.Index(fields=["source_type", "source_id"], name="netbox_acls_source__01d2fa_idx")],
            },
        ),
    ]
