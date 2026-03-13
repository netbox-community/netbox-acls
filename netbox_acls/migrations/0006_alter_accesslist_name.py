import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_acls", "0005_preflight_validate_upgrade"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accesslist",
            name="name",
            field=models.CharField(
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
    ]
