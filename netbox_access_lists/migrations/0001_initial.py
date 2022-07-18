import django.contrib.postgres.fields
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0072_created_datetimefield'),
        ('ipam', '0057_created_datetimefield'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access_lists', to='dcim.device')),
                ('type', models.CharField(max_length=100)),
                ('default_action', models.CharField(max_length=30)),
                ('comments', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name', 'device'),
                'unique_together': {('name', 'device')},
            },
        ),
        migrations.CreateModel(
            name='ACLStandardRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('index', models.PositiveIntegerField()),
                ('access_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aclstandardrules', to='netbox_access_lists.accesslist')),
                ('remark', models.CharField(blank=True, null=True, max_length=500)),
                ('action', models.CharField(blank=True, null=True, max_length=30)),
                ('source_prefix', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='ipam.prefix')),
            ],
            options={
                'ordering': ('access_list', 'index'),
                'unique_together': {('access_list', 'index')},
            },
        ),
        migrations.CreateModel(
            name='ACLExtendedRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('index', models.PositiveIntegerField()),
                ('access_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aclextendedrules', to='netbox_access_lists.accesslist')),
                ('remark', models.CharField(blank=True, null=True, max_length=500)),
                ('action', models.CharField(blank=True, null=True, max_length=30)),
                ('source_prefix', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='ipam.prefix')),
                ('source_ports', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), blank=True, null=True, size=None)),
                ('destination_prefix', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='ipam.prefix')),
                ('destination_ports', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), blank=True, null=True, size=None)),
                ('protocol', models.CharField(blank=True, max_length=30)),
            ],
            options={
                'ordering': ('access_list', 'index'),
                'unique_together': {('access_list', 'index')},
            },
        ),
    ]
