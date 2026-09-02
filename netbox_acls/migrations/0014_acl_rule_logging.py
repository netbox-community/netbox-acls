import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0001_squashed_0013_acl_owner"),
    ]

    operations = [
        migrations.AddField(
            model_name="aclextendedrule",
            name="log_matches",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="aclextendedrule",
            name="log_options",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100), blank=True, default=list
            ),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="log_matches",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="aclstandardrule",
            name="log_options",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100), blank=True, default=list
            ),
        ),
    ]
