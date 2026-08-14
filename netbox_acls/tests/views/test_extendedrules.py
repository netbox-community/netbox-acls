from django.contrib.contenttypes.models import ContentType
from django.db.backends.postgresql.psycopg_any import NumericRange
from netaddr import IPNetwork

from ipam.models import Prefix
from utilities.testing import create_tags

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...models import AccessList, ACLExtendedRule
from ...utils import normalize_port_ranges
from .base import ACLRuleSequenceTestsMixin, PluginTestCases, build_ipam_objects


class ACLExtendedRuleViewTestCase(ACLRuleSequenceTestsMixin, PluginTestCases.ObjectViewTestCase):
    """View tests for ACLExtendedRule."""

    model = ACLExtendedRule
    add_permission = "netbox_acls.add_aclextendedrule"
    change_permission = "netbox_acls.change_aclextendedrule"
    user_permissions = (
        "ipam.view_aggregate",
        "ipam.view_ipaddress",
        "ipam.view_iprange",
        "ipam.view_prefix",
        "netbox_acls.view_accesslist",
    )

    @classmethod
    def setUpTestData(cls):
        aggregate, cls.source_prefix, ip_address, ip_range = build_ipam_objects()
        cls.destination_prefix = Prefix.objects.create(prefix=IPNetwork("10.2.0.0/16"))

        cls.access_list = AccessList.objects.create(
            name="testextendedacl",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        # Stored half-open, so an inclusive 80 to 80 becomes [80, 81).
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=10,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            source=cls.source_prefix,
            destination=cls.destination_prefix,
            source_port_ranges=normalize_port_ranges([NumericRange(1024, 2048, bounds="[]")]),
            destination_port_ranges=normalize_port_ranges([NumericRange(80, 80, bounds="[]")]),
            description="permit web",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=20,
            action=ACLRuleActionChoices.ACTION_DENY,
            protocol=ACLProtocolChoices.PROTOCOL_UDP,
            source=ip_address,
            destination=ip_range,
            destination_port_ranges=normalize_port_ranges([NumericRange(53, 53, bounds="[]")]),
            description="deny dns",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=30,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            protocol=ACLProtocolChoices.PROTOCOL_ICMP,
            source=aggregate,
            destination=ip_address,
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=40,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="an extended remark",
        )
        ACLExtendedRule.objects.create(
            access_list=cls.access_list,
            sequence=50,
            action=ACLRuleActionChoices.ACTION_DENY,
            protocol=ACLProtocolChoices.PROTOCOL_IP,
            source=ip_range,
            destination=aggregate,
            description="deny the range",
        )

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # Ports are posted inclusively and need protocol tcp or udp. These values
        # round-trip unchanged: no single ports, no adjacent pairs to merge.
        cls.form_data = {
            "access_list": cls.access_list.pk,
            "sequence": 60,
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "remark": "",
            "protocol": ACLProtocolChoices.PROTOCOL_TCP,
            "source_type": ContentType.objects.get_for_model(Prefix).pk,
            "source": cls.source_prefix.pk,
            "source_port_ranges": "1024-2048",
            "destination_type": ContentType.objects.get_for_model(Prefix).pk,
            "destination": cls.destination_prefix.pk,
            "destination_port_ranges": "8080-8081",
            "description": "A new extended rule",
            "comments": "",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Bulk edited",
        }
