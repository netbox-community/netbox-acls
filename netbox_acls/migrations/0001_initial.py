"""
Defines the migrations for propogating django models into the database schemea.
"""

import django.contrib.postgres.fields
import django.core.serializers.json
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

__all__ = ("Migration",)


class Migration(migrations.Migration):
    """
    Defines the migrations required for the initial setup of the access lists plugin and its associated django models.
    """

    initial = True

    dependencies = [
        ("extras", "0072_created_datetimefield"),
        ("ipam", "0057_created_datetimefield"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessList",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=500)),
                ("assigned_object_id", models.PositiveIntegerField()),
                (
                    "assigned_object_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.contenttype",
                    ),
                ),
                ("type", models.CharField(max_length=100)),
                ("default_action", models.CharField(default="deny", max_length=30)),
                ("comments", models.TextField(blank=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem",
                        to="extras.Tag",
                    ),
                ),
            ],
            options={
                "ordering": ("name", "device"),
                "unique_together": {
                    ("assigned_object_type", "assigned_object_id", "name"),
                },
                "verbose_name": "Access List",
            },
        ),
        migrations.CreateModel(
            name="ACLInterfaceAssignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "access_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aclinterfaceassignment",
                        to="netbox_acls.accesslist",
                    ),
                ),
                ("direction", models.CharField(max_length=100)),
                ("assigned_object_id", models.PositiveIntegerField()),
                (
                    "assigned_object_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.contenttype",
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem",
                        to="extras.Tag",
                    ),
                ),
            ],
            options={
                "ordering": (
                    "access_list",
                    "assigned_object_type",
                    "assigned_object_id",
                    "direction",
                ),
                "unique_together": {
                    (
                        "assigned_object_type",
                        "assigned_object_id",
                        "access_list",
                        "direction",
                    ),
                },
                "verbose_name": "ACL Interface Assignment",
            },
        ),
        migrations.CreateModel(
            name="ACLStandardRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem",
                        to="extras.Tag",
                    ),
                ),
                (
                    "access_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aclstandardrules",
                        to="netbox_acls.accesslist",
                    ),
                ),
                ("index", models.PositiveIntegerField()),
                ("description", models.CharField(blank=True, max_length=500)),
                ("action", models.CharField(max_length=30)),
                ("remark", models.CharField(blank=True, null=True, max_length=500)),
                (
                    "source_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="ipam.prefix",
                    ),
                ),
            ],
            options={
                "ordering": ("access_list", "index"),
                "unique_together": {("access_list", "index")},
                "verbose_name": "ACL Standard Rule",
            },
        ),
        migrations.CreateModel(
            name="ACLExtendedRule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem",
                        to="extras.Tag",
                    ),
                ),
                (
                    "access_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aclstandardrules",
                        to="netbox_acls.accesslist",
                    ),
                ),
                ("index", models.PositiveIntegerField()),
                ("description", models.CharField(blank=True, max_length=500)),
                ("action", models.CharField(max_length=30)),
                ("remark", models.CharField(blank=True, null=True, max_length=500)),
                (
                    "source_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="ipam.prefix",
                    ),
                ),
                (
                    "source_ports",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveIntegerField(),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "destination_prefix",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="ipam.prefix",
                    ),
                ),
                (
                    "destination_ports",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveIntegerField(),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                ("protocol", models.CharField(blank=True, max_length=30)),
            ],
            options={
                "ordering": ("access_list", "index"),
                "unique_together": {("access_list", "index")},
                "verbose_name": "ACL Extended Rule",
            },
        ),
        # migrations.AddConstraint(
        #     model_name="accesslist",
        #     constraint=models.UniqueConstraint(
        #         fields=("assigned_object_type", "assigned_object_id"), name="accesslist_assigned_object"
        #     ),
        # ),
    ]
