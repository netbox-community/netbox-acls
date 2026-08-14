from django.contrib.contenttypes.models import ContentType

from ipam.models import Prefix
from utilities.testing import create_tags

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLStandardRule
from .base import ACLRuleSequenceTestsMixin, PluginTestCases, build_ipam_objects


class ACLStandardRuleViewTestCase(ACLRuleSequenceTestsMixin, PluginTestCases.ObjectViewTestCase):
    """View tests for ACLStandardRule."""

    model = ACLStandardRule
    add_permission = "netbox_acls.add_aclstandardrule"
    change_permission = "netbox_acls.change_aclstandardrule"
    user_permissions = (
        "ipam.view_aggregate",
        "ipam.view_ipaddress",
        "ipam.view_iprange",
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        aggregate, cls.prefix, ip_address, ip_range = build_ipam_objects()

        cls.access_list = AccessList.objects.create(
            name="teststandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # create() not bulk_create(): save() populates the _source_* columns.
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=cls.prefix,
            description="permit the prefix",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=ip_address,
            description="deny the address",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=30,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=ip_range,
            description="deny the range",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=40,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="a standard remark",
        )
        ACLStandardRule.objects.create(
            access_list=cls.access_list,
            sequence=50,
            action=ACLRuleActionChoices.ACTION_DENY,
            source=aggregate,
            description="deny the aggregate",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "access_list": cls.access_list.pk,
            "sequence": 60,
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "remark": "",
            "source_type": ContentType.objects.get_for_model(Prefix).pk,
            "source": cls.prefix.pk,
            "description": "A new standard rule",
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Bulk edited",
        }
