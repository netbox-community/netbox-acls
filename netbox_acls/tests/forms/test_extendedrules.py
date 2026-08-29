from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Prefix

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ...constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from ...forms import ACLExtendedRuleBulkEditForm, ACLExtendedRuleFilterForm, ACLExtendedRuleForm
from ...models import AccessList, ACLExtendedRule
from ..views.base import build_ipam_objects
from .base import BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin


class ACLExtendedRuleFormTestCase(BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin, TestCase):
    """Form tests for ACLExtendedRule forms."""

    bulk_edit_form = ACLExtendedRuleBulkEditForm
    filter_form = ACLExtendedRuleFilterForm

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
            "source_content_type": ContentType.objects.get_for_model(Prefix).pk,
            "source_object_id": self.prefix.pk,
            "destination_content_type": ContentType.objects.get_for_model(Prefix).pk,
            "destination_object_id": self.destination_prefix.pk,
        }
        data.update(overrides)
        return ACLExtendedRuleForm(data=data)

    def _rule(self, sequence):
        return ACLExtendedRule.objects.create(
            access_list=self.access_list,
            sequence=sequence,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix,
            destination=self.destination_prefix,
        )

    def test_instance_seeds_both_object_fields(self):
        """Both roles reach the form as initial values, not just the source."""
        form = ACLExtendedRuleForm(instance=self._rule(10))
        self.assertEqual(form.initial["source"], self.prefix)
        self.assertEqual(form.initial["destination"], self.destination_prefix)

    def test_editing_keeps_the_unchanged_role_and_clears_the_switched_one(self):
        """Test that an edit holds the role whose type is unchanged and drops the switched one."""
        # Values arrive as text, the way a browser posts them.
        rule = self._rule(20)
        form = ACLExtendedRuleForm(
            data={
                "access_list": str(self.access_list.pk),
                "sequence": "20",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_content_type": str(ContentType.objects.get_for_model(Prefix).pk),
                "source_object_id": str(self.prefix.pk),
                "destination_content_type": str(ContentType.objects.get_for_model(self.ip_address).pk),
            },
            instance=rule,
        )
        self.assertIs(form.fields["source"].selected_model, Prefix)
        self.assertTrue(form.fields["source"].object_field.queryset.exists())
        destination = form.fields["destination"]
        self.assertIs(destination.selected_model, type(self.ip_address))
        self.assertFalse(destination.object_field.queryset.exists())

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
                    source_content_type=ContentType.objects.get_for_model(source).pk,
                    source_object_id=source.pk,
                )
                field = form.fields["source"]
                self.assertIs(field.selected_model, type(source))
                self.assertEqual(field.queryset.model, type(source))

    def test_destination_queryset_follows_type(self):
        """Test that the destination picker's queryset is resolved from the posted type."""
        for destination in (self.aggregate, self.prefix, self.ip_address, self.ip_range):
            with self.subTest(destination=destination._meta.label_lower):
                form = self._bound_form(
                    destination_content_type=ContentType.objects.get_for_model(destination).pk,
                    destination_object_id=destination.pk,
                )
                field = form.fields["destination"]
                self.assertIs(field.selected_model, type(destination))
                self.assertEqual(field.queryset.model, type(destination))

    def test_source_type_choices_limited(self):
        """Test that the source type picker offers only the ipam models a rule accepts."""
        form = ACLExtendedRuleForm()
        self.assertQuerySetEqual(
            form.fields["source"].content_type_field.queryset.order_by("pk"),
            ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS).order_by("pk"),
            transform=lambda ct: ct,
        )

    def test_destination_type_choices_limited(self):
        """Test that the destination type picker offers only the ipam models a rule accepts."""
        form = ACLExtendedRuleForm()
        self.assertQuerySetEqual(
            form.fields["destination"].content_type_field.queryset.order_by("pk"),
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

    def test_bulkedit_type_widgets_swap_the_form_fields(self):
        """Test that both bulk-edit type pickers post and swap, for either role."""
        form = ACLExtendedRuleBulkEditForm()
        for role in ("source", "destination"):
            with self.subTest(role=role):
                attrs = form.fields[f"{role}_type"].widget.attrs
                self.assertEqual(attrs["hx-post"], ".")
                self.assertEqual(attrs["hx-select"], "#form_fields")

    def test_bulkedit_labels_follow_type(self):
        """Test that each role's resolved label names that role, so the two cannot be confused."""
        form = ACLExtendedRuleBulkEditForm(
            data={
                "source_type": ContentType.objects.get_for_model(self.ip_range).pk,
                "destination_type": ContentType.objects.get_for_model(self.aggregate).pk,
            },
        )
        self.assertEqual(form.fields["source"].label, "Source IP Range")
        self.assertEqual(form.fields["destination"].label, "Destination Aggregate")

    def test_bulkedit_nullable_fields(self):
        """Test that the nullable list stays exhaustive for this form."""
        self.assertEqual(
            ACLExtendedRuleBulkEditForm.nullable_fields,
            (
                "remark",
                "source_type",
                "source",
                "destination_type",
                "destination",
                "description",
                "comments",
            ),
        )

    def test_filterform_access_list_filtered_to_extended(self):
        """Test that the filter form's Access List picker filters to Extended ACLs."""
        form = ACLExtendedRuleFilterForm()
        self.assertEqual(
            form.fields["access_list_id"].query_params,
            {"type": ACLTypeChoices.TYPE_EXTENDED},
        )

    def test_protocol_filter_form_accepts_a_grouped_value(self):
        """add_blank_choice concatenates tuples, so the optgroups must survive into the field."""
        form = ACLExtendedRuleFilterForm(data={"protocol": ACLProtocolChoices.PROTOCOL_GRE})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["protocol"], ACLProtocolChoices.PROTOCOL_GRE)

    def test_logging_fields_are_present(self):
        """Test that the model form exposes both logging fields."""
        form = ACLExtendedRuleForm()
        self.assertIn("log_matches", form.fields)
        self.assertIn("log_options", form.fields)

    def test_form_rejects_options_without_log_matches(self):
        """Test that the model form surfaces the consistency error per field."""
        form = self._bound_form(log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG])
        self.assertFalse(form.is_valid())
        self.assertIn("log_options", form.errors)

    def test_bulkedit_disabling_logging_clears_the_options(self):
        """Test that turning logging off also drops the options."""
        form = ACLExtendedRuleBulkEditForm(
            data={"log_matches": "False", "pk": [self._rule(10).pk]},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["log_options"], [])
        self.assertIn("log_options", form.changed_data)

    def test_bulkedit_clear_rejects_an_explicit_selection(self):
        """Test that clearing and selecting log options at once is rejected."""
        form = ACLExtendedRuleBulkEditForm(
            data={
                "clear_log_options": True,
                "log_options": [ACLRuleLogOptionChoices.OPTION_SYSLOG],
                "pk": [self._rule(20).pk],
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("clear_log_options", form.errors)

    def test_bulkedit_disabling_logging_rejects_a_selection(self):
        """Test that disabling logging while selecting options is rejected."""
        form = ACLExtendedRuleBulkEditForm(
            data={
                "log_matches": "False",
                "log_options": [ACLRuleLogOptionChoices.OPTION_SYSLOG],
                "pk": [self._rule(30).pk],
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("log_options", form.errors)
