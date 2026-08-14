from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Prefix

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLTypeChoices,
)
from ...constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from ...forms import ACLExtendedRuleBulkEditForm, ACLExtendedRuleForm
from ...models import AccessList
from ..views.base import build_ipam_objects
from .base import BulkEditFieldsetTestMixin


class ACLExtendedRuleFormTestCase(BulkEditFieldsetTestMixin, TestCase):
    """Form tests for ACLExtendedRule forms."""

    bulk_edit_form = ACLExtendedRuleBulkEditForm

    @classmethod
    def setUpTestData(cls):
        cls.aggregate, cls.prefix, cls.ip_address, cls.ip_range = build_ipam_objects()
        cls.destination_prefix = Prefix.objects.create(prefix=IPNetwork("10.2.0.0/16"))
        cls.access_list = AccessList.objects.create(
            name="testextendedacl",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

    def _bound_form(self, **overrides):
        """Bind the form, so the posted types reach __init__."""
        data = {
            "access_list": self.access_list.pk,
            "sequence": 10,
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "protocol": ACLProtocolChoices.PROTOCOL_TCP,
            "source_type": ContentType.objects.get_for_model(Prefix).pk,
            "source": self.prefix.pk,
            "destination_type": ContentType.objects.get_for_model(Prefix).pk,
            "destination": self.destination_prefix.pk,
        }
        data.update(overrides)
        return ACLExtendedRuleForm(data=data)

    def test_bulkedit_access_list_filtered_to_extended(self):
        """#360: the extended bulk-edit Access List picker must filter to Extended ACLs."""
        form = ACLExtendedRuleBulkEditForm()
        self.assertEqual(
            form.fields["access_list"].query_params,
            {"type": ACLTypeChoices.TYPE_EXTENDED},
        )

    def test_access_list_queryset_limited_to_extended(self):
        """Test that the model form's Access List picker filters to Extended ACLs."""
        form = ACLExtendedRuleForm()
        self.assertEqual(
            form.fields["access_list"].query_params,
            {"type": ACLTypeChoices.TYPE_EXTENDED},
        )

    def test_source_queryset_follows_type(self):
        """Test that the source picker's queryset is resolved from the posted source type."""
        for source in (self.aggregate, self.prefix, self.ip_address, self.ip_range):
            with self.subTest(source=source._meta.label_lower):
                form = self._bound_form(
                    source_type=ContentType.objects.get_for_model(source).pk,
                    source=source.pk,
                )
                self.assertEqual(form.fields["source"].queryset.model, type(source))
                self.assertFalse(form.fields["source"].disabled)

    def test_destination_queryset_follows_type(self):
        """Test that the destination picker's queryset is resolved from the posted type."""
        for destination in (self.aggregate, self.prefix, self.ip_address, self.ip_range):
            with self.subTest(destination=destination._meta.label_lower):
                form = self._bound_form(
                    destination_type=ContentType.objects.get_for_model(destination).pk,
                    destination=destination.pk,
                )
                self.assertEqual(form.fields["destination"].queryset.model, type(destination))
                self.assertFalse(form.fields["destination"].disabled)

    def test_source_type_choices_limited(self):
        """Test that the source type picker offers only the ipam models a rule accepts."""
        form = ACLExtendedRuleForm()
        self.assertQuerySetEqual(
            form.fields["source_type"].queryset.order_by("pk"),
            ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS).order_by("pk"),
            transform=lambda ct: ct,
        )

    def test_destination_type_choices_limited(self):
        """Test that the destination type picker offers only the ipam models a rule accepts."""
        form = ACLExtendedRuleForm()
        self.assertQuerySetEqual(
            form.fields["destination_type"].queryset.order_by("pk"),
            ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS).order_by("pk"),
            transform=lambda ct: ct,
        )

    def test_clean_assigns_source_and_destination(self):
        """Test that a valid form assigns both selected objects to the instance."""
        form = self._bound_form()
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertEqual(form.instance.source, self.prefix)
        self.assertEqual(form.instance.destination, self.destination_prefix)

    def test_bulkedit_source_and_destination_querysets_follow_type(self):
        """Test that the bulk-edit pickers' querysets are resolved from the posted types."""
        prefix_type = ContentType.objects.get_for_model(Prefix).pk
        form = ACLExtendedRuleBulkEditForm(
            data={"source_type": prefix_type, "destination_type": prefix_type},
        )
        self.assertEqual(form.fields["source"].queryset.model, Prefix)
        self.assertFalse(form.fields["source"].disabled)
        self.assertEqual(form.fields["destination"].queryset.model, Prefix)
        self.assertFalse(form.fields["destination"].disabled)

    def test_port_ranges_round_trip_inclusive(self):
        """Test that port ranges posted inclusively are stored half-open and shown inclusively."""
        form = self._bound_form(source_port_ranges="80-81", destination_port_ranges="8080-8081")
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        instance = form.save()
        self.assertEqual(
            [(r.lower, r.upper) for r in instance.source_port_ranges],
            [(80, 82)],
        )
        self.assertEqual(instance.source_port_ranges_list, ["80-81"])
        self.assertEqual(instance.destination_port_ranges_list, ["8080-8081"])
