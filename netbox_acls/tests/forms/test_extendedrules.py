from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Prefix

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLICMPTypeChoices,
    ACLICMPv4TypeChoices,
    ACLICMPv6TypeChoices,
    ACLProtocolChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTCPFlagChoices,
    ACLTCPFlagMatchChoices,
    ACLTypeChoices,
)
from ...constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from ...forms import (
    ACLExtendedRuleBulkEditForm,
    ACLExtendedRuleFilterForm,
    ACLExtendedRuleForm,
    ACLExtendedRuleImportForm,
)
from ...models import AccessList, ACLAddressGroup, ACLExtendedRule
from ..views.base import build_ipam_objects
from .base import BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin

UNRESOLVABLE_OBJECT_ID = 99999999


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

    def _bound_form(self, instance=None, **overrides):
        """Bind the form, so the posted types reach __init__."""
        data = {
            "access_list": self.access_list.pk,
            "sequence": 10,
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "protocol": ACLProtocolChoices.PROTOCOL_TCP,
            "tcp_flags_match": ACLTCPFlagMatchChoices.MATCH_ALL,
            "source_content_type": ContentType.objects.get_for_model(Prefix).pk,
            "source_object_id": self.prefix.pk,
            "destination_content_type": ContentType.objects.get_for_model(Prefix).pk,
            "destination_object_id": self.destination_prefix.pk,
        }
        data.update(overrides)
        return ACLExtendedRuleForm(data=data, instance=instance)

    def _rule(self, sequence, **overrides):
        values = {
            "access_list": self.access_list,
            "sequence": sequence,
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "source": self.prefix,
            "destination": self.destination_prefix,
        }
        values.update(overrides)
        return ACLExtendedRule.objects.create(**values)

    def test_instance_seeds_both_object_fields(self):
        """Both roles reach the form as initial values, not just the source."""
        form = ACLExtendedRuleForm(instance=self._rule(10))
        self.assertEqual(form.initial["source"], self.prefix)
        self.assertEqual(form.initial["destination"], self.destination_prefix)

    def test_editing_keeps_a_complete_role_and_rejects_an_incomplete_one(self):
        """Test that the two roles are validated independently on an edit."""
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
        self.assertIs(form.fields["destination"].selected_model, type(self.ip_address))
        # A type with no object is a validation error rather than a silent clear.
        self.assertFalse(form.is_valid())
        self.assertIn("destination", form.errors)
        self.assertNotIn("source", form.errors)

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
        form = ACLExtendedRuleForm(initial={"action": ACLRuleActionChoices.ACTION_PERMIT})
        self.assertQuerySetEqual(
            form.fields["source"].content_type_field.queryset.order_by("pk"),
            ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS).order_by("pk"),
            transform=lambda ct: ct,
        )

    def test_destination_type_choices_limited(self):
        """Test that the destination type picker offers only the ipam models a rule accepts."""
        form = ACLExtendedRuleForm(initial={"action": ACLRuleActionChoices.ACTION_PERMIT})
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

    def test_clean_assigns_address_group_source_and_destination(self):
        """Test that a valid form assigns selected address groups to both roles."""
        address_group = ACLAddressGroup.objects.create(name="address-group-1")
        address_group_type = ContentType.objects.get_for_model(ACLAddressGroup).pk
        form = self._bound_form(
            source_content_type=address_group_type,
            source_object_id=address_group.pk,
            destination_content_type=address_group_type,
            destination_object_id=address_group.pk,
        )
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertEqual(form.instance.source, address_group)
        self.assertEqual(form.instance.destination, address_group)

    def test_bulkedit_source_and_destination_querysets_follow_type(self):
        """Test that the bulk-edit pickers' querysets are resolved from the posted types."""
        prefix_type = ContentType.objects.get_for_model(Prefix).pk
        form = ACLExtendedRuleBulkEditForm(
            data={"source_content_type": prefix_type, "destination_content_type": prefix_type},
        )
        for role in ("source", "destination"):
            with self.subTest(role=role):
                self.assertIs(form.fields[role].selected_model, Prefix)
                self.assertEqual(form.fields[role].queryset.model, Prefix)

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
                attrs = form.fields[role].content_type_field.widget.attrs
                self.assertEqual(attrs["hx-post"], ".")
                self.assertEqual(attrs["hx-select"], "#form_fields")

    def test_bulkedit_labels_name_the_role(self):
        """Test that each label names its role, so the two pickers cannot be confused."""
        form = ACLExtendedRuleBulkEditForm(
            data={
                "source_content_type": ContentType.objects.get_for_model(self.ip_range).pk,
                "destination_content_type": ContentType.objects.get_for_model(self.aggregate).pk,
            },
        )
        self.assertEqual(form.fields["source"].label, "Source")
        self.assertEqual(form.fields["destination"].label, "Destination")

    def test_bulkedit_nullable_fields(self):
        """Test that the nullable list stays exhaustive for this form."""
        self.assertEqual(
            ACLExtendedRuleBulkEditForm.nullable_fields,
            ("remark", "source", "destination", "icmp_type", "icmp_code", "description", "comments"),
        )

    def test_filterform_access_list_filtered_to_extended(self):
        """Test that the filter form's Access List picker filters to Extended ACLs."""
        form = ACLExtendedRuleFilterForm()
        self.assertEqual(
            form.fields["access_list_id"].query_params,
            {"type": ACLTypeChoices.TYPE_EXTENDED},
        )

    def test_choice_filters_accept_multiple_values(self):
        """The filter form's choice fields must be multi-selects, matching the filter set."""
        form = ACLExtendedRuleFilterForm()
        for field_name in ("action", "protocol", "tcp_flags", "tcp_flags_match"):
            with self.subTest(field_name=field_name):
                self.assertIsInstance(form.fields[field_name], forms.MultipleChoiceField)

    def test_protocol_filter_form_accepts_a_grouped_value(self):
        """ACLProtocolChoices is optgrouped, so the groups must survive into the field."""
        form = ACLExtendedRuleFilterForm(data={"protocol": [ACLProtocolChoices.PROTOCOL_GRE]})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["protocol"], [ACLProtocolChoices.PROTOCOL_GRE])

    def test_filterform_icmp_type_offers_the_family_labelled_presets(self):
        """Test that the filter form's ICMP type offers the presets of both families."""
        form = ACLExtendedRuleFilterForm()
        self.assertIs(form.fields["icmp_type"].widget.original_widget.options, ACLICMPTypeChoices)

    def test_logging_fields_are_present(self):
        """Test that the model form exposes both logging fields."""
        form = ACLExtendedRuleForm(initial={"action": ACLRuleActionChoices.ACTION_PERMIT})
        self.assertIn("log_matches", form.fields)
        self.assertIn("log_options", form.fields)

    def test_form_keeps_an_icmp_type_and_code_of_zero(self):
        """Test that the model form passes an ICMP type and code of zero to the rule."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_ICMP, icmp_type=0, icmp_code=0)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertEqual((form.instance.icmp_type, form.instance.icmp_code), (0, 0))

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

    def test_remark_action_removes_the_match_criteria(self):
        """Test that a remark rule's form hides the match criteria and logging but keeps the remark."""
        form = self._bound_form(action=ACLRuleActionChoices.ACTION_REMARK, remark="Note")
        for field_name in (
            "source",
            "source_port_ranges",
            "destination",
            "destination_port_ranges",
            "protocol",
            "icmp_type",
            "icmp_code",
            "tcp_flags",
            "tcp_flags_match",
            "log_matches",
            "log_options",
        ):
            with self.subTest(field_name=field_name):
                self.assertNotIn(field_name, form.fields)
        self.assertIn("remark", form.fields)

    def test_blank_action_removes_the_match_criteria(self):
        """Test that a new rule's form offers no match criteria until an action is picked."""
        form = ACLExtendedRuleForm()
        for field_name in (
            "source",
            "source_port_ranges",
            "destination",
            "destination_port_ranges",
            "protocol",
            "icmp_type",
            "icmp_code",
            "tcp_flags",
            "tcp_flags_match",
            "log_matches",
            "log_options",
        ):
            with self.subTest(field_name=field_name):
                self.assertNotIn(field_name, form.fields)
        self.assertIn("remark", form.fields)

    def test_cleared_action_removes_the_match_criteria(self):
        """Test that an edited rule's form offers no match criteria once its action is cleared."""
        form = self._bound_form(instance=self._rule(10), action="")
        for field_name in (
            "source",
            "source_port_ranges",
            "destination",
            "destination_port_ranges",
            "protocol",
            "icmp_type",
            "icmp_code",
            "tcp_flags",
            "tcp_flags_match",
            "log_matches",
            "log_options",
        ):
            with self.subTest(field_name=field_name):
                self.assertNotIn(field_name, form.fields)
        self.assertIn("remark", form.fields)

    def test_deny_action_keeps_the_match_criteria(self):
        """Test that a deny rule's form offers every match criterion."""
        form = self._bound_form(action=ACLRuleActionChoices.ACTION_DENY)
        for field_name in (
            "source",
            "source_port_ranges",
            "destination",
            "destination_port_ranges",
            "protocol",
            "tcp_flags",
            "tcp_flags_match",
            "log_matches",
            "log_options",
        ):
            with self.subTest(field_name=field_name):
                self.assertIn(field_name, form.fields)

    def test_remark_action_drops_the_emptied_fieldsets(self):
        """Test that a remark rule's form keeps only the fieldsets with a field left."""
        form = self._bound_form(action=ACLRuleActionChoices.ACTION_REMARK, remark="Note")
        self.assertEqual(
            [str(fieldset.name) for fieldset in form.fieldsets],
            ["Access List Details", "Rule Definition", "Remark"],
        )

    def test_tcp_rule_offers_the_tcp_flags_fieldset(self):
        """Test that a TCP rule's form shows the TCP Flags fieldset and drops the ICMP one."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_TCP)
        self.assertEqual(
            [str(fieldset.name) for fieldset in form.fieldsets],
            [
                "Access List Details",
                "Rule Definition",
                "Remark",
                "Protocol",
                "Source Definition",
                "Destination Definition",
                "TCP Flags",
                "Logging",
            ],
        )

    def test_icmp_rule_offers_the_icmp_fieldset(self):
        """Test that an ICMP rule's form shows the ICMP fieldset and drops the TCP Flags one."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_ICMP)
        self.assertEqual(
            [str(fieldset.name) for fieldset in form.fieldsets],
            [
                "Access List Details",
                "Rule Definition",
                "Remark",
                "Protocol",
                "Source Definition",
                "Destination Definition",
                "ICMP",
                "Logging",
            ],
        )

    def test_icmpv4_protocol_offers_the_icmpv4_type_presets(self):
        """Test that an ICMPv4 rule's type field offers the ICMPv4 presets."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_ICMPV4)
        self.assertIs(form.fields["icmp_type"].widget.options, ACLICMPv4TypeChoices)

    def test_icmpv6_protocol_offers_the_icmpv6_type_presets(self):
        """Test that an ICMPv6 rule's type field offers the ICMPv6 presets."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_ICMPV6)
        self.assertIs(form.fields["icmp_type"].widget.options, ACLICMPv6TypeChoices)

    def test_icmp_protocol_offers_the_family_labelled_type_presets(self):
        """Test that an ICMP rule's type field offers the presets of both families."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_ICMP)
        self.assertIs(form.fields["icmp_type"].widget.options, ACLICMPTypeChoices)

    def test_family_labelled_type_presets_name_both_families(self):
        """Test that the combined presets carry each family's number under its family label."""
        self.assertIn((8, "ICMPv4: Echo request (8)"), ACLICMPTypeChoices.CHOICES)
        self.assertIn((128, "ICMPv6: Echo request (128)"), ACLICMPTypeChoices.CHOICES)

    def test_icmp_protocol_removes_the_port_fields(self):
        """Test that an ICMP rule's form hides both port fields and keeps both objects."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_ICMP)
        self.assertNotIn("source_port_ranges", form.fields)
        self.assertNotIn("destination_port_ranges", form.fields)
        self.assertIn("source", form.fields)
        self.assertIn("destination", form.fields)

    def test_udp_protocol_keeps_the_port_fields(self):
        """Test that a UDP rule's form keeps both port fields."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_UDP)
        self.assertIn("source_port_ranges", form.fields)
        self.assertIn("destination_port_ranges", form.fields)

    def test_blank_protocol_removes_the_port_fields(self):
        """Test that a rule without a protocol offers no port fields."""
        form = self._bound_form(protocol="")
        self.assertNotIn("source_port_ranges", form.fields)
        self.assertNotIn("destination_port_ranges", form.fields)

    def test_icmp_protocols_keep_the_icmp_fields(self):
        """Test that an ICMP, ICMPv4 or ICMPv6 rule's form offers the ICMP type and code."""
        for protocol in (
            ACLProtocolChoices.PROTOCOL_ICMP,
            ACLProtocolChoices.PROTOCOL_ICMPV4,
            ACLProtocolChoices.PROTOCOL_ICMPV6,
        ):
            with self.subTest(protocol=protocol):
                form = self._bound_form(protocol=protocol)
                self.assertIn("icmp_type", form.fields)
                self.assertIn("icmp_code", form.fields)

    def test_other_protocols_remove_the_icmp_fields(self):
        """Test that every protocol other than the ICMP ones hides the ICMP type and code."""
        icmp_protocols = {
            ACLProtocolChoices.PROTOCOL_ICMP,
            ACLProtocolChoices.PROTOCOL_ICMPV4,
            ACLProtocolChoices.PROTOCOL_ICMPV6,
        }
        other_protocols = [protocol for protocol in ACLProtocolChoices.values() if protocol not in icmp_protocols]
        self.assertIn(ACLProtocolChoices.PROTOCOL_IP, other_protocols)
        for protocol in other_protocols:
            with self.subTest(protocol=protocol):
                form = self._bound_form(protocol=protocol)
                self.assertNotIn("icmp_type", form.fields)
                self.assertNotIn("icmp_code", form.fields)

    def test_tcp_protocol_keeps_the_tcp_flag_fields(self):
        """Test that a TCP rule's form offers the TCP flags and their match mode."""
        form = self._bound_form(protocol=ACLProtocolChoices.PROTOCOL_TCP)
        self.assertIn("tcp_flags", form.fields)
        self.assertIn("tcp_flags_match", form.fields)

    def test_other_protocols_remove_the_tcp_flag_fields(self):
        """Test that every protocol other than TCP hides the TCP flags and their match mode."""
        other_protocols = [
            protocol for protocol in ACLProtocolChoices.values() if protocol != ACLProtocolChoices.PROTOCOL_TCP
        ]
        self.assertIn(ACLProtocolChoices.PROTOCOL_IP, other_protocols)
        for protocol in other_protocols:
            with self.subTest(protocol=protocol):
                form = self._bound_form(protocol=protocol)
                self.assertNotIn("tcp_flags", form.fields)
                self.assertNotIn("tcp_flags_match", form.fields)

    def test_blank_protocol_removes_the_icmp_and_tcp_flag_fields(self):
        """Test that a rule without a protocol offers no ICMP or TCP flag fields."""
        form = self._bound_form(protocol="")
        for field_name in ("icmp_type", "icmp_code", "tcp_flags", "tcp_flags_match"):
            with self.subTest(field_name=field_name):
                self.assertNotIn(field_name, form.fields)

    def test_blank_protocol_saves_as_an_empty_string(self):
        """Test that a rule saved without a protocol stores an empty string."""
        form = self._bound_form(protocol="")
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        rule = form.save()
        rule.refresh_from_db()
        self.assertEqual(rule.protocol, "")

    def test_unbound_form_follows_the_stored_protocol(self):
        """Test that the edit form of a stored UDP rule offers both port fields."""
        form = ACLExtendedRuleForm(instance=self._rule(10, protocol=ACLProtocolChoices.PROTOCOL_UDP))
        self.assertIn("source_port_ranges", form.fields)
        self.assertIn("destination_port_ranges", form.fields)

    def test_redraw_initial_overrides_the_stored_protocol(self):
        """Test that the protocol of a redraw wins over the stored one."""
        form = ACLExtendedRuleForm(
            instance=self._rule(10, protocol=ACLProtocolChoices.PROTOCOL_TCP),
            initial={"protocol": ACLProtocolChoices.PROTOCOL_ICMP},
        )
        self.assertNotIn("source_port_ranges", form.fields)
        self.assertNotIn("destination_port_ranges", form.fields)

    def test_switching_to_icmp_clears_the_stored_ports(self):
        """Test that saving a TCP rule as ICMP clears its stored ports."""
        rule = self._rule(
            10,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            source_port_ranges=[NumericRange(22, 23)],
            destination_port_ranges=[NumericRange(443, 444)],
        )
        form = self._bound_form(instance=rule, protocol=ACLProtocolChoices.PROTOCOL_ICMP)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        form.save()
        rule.refresh_from_db()
        self.assertEqual(rule.source_port_ranges, [])
        self.assertEqual(rule.destination_port_ranges, [])

    def test_switching_to_no_protocol_clears_the_stored_ports(self):
        """Test that saving a TCP rule without a protocol clears its stored ports."""
        rule = self._rule(
            10,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            source_port_ranges=[NumericRange(22, 23)],
            destination_port_ranges=[NumericRange(443, 444)],
        )
        form = self._bound_form(instance=rule, protocol="")
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        form.save()
        rule.refresh_from_db()
        self.assertEqual(rule.source_port_ranges, [])
        self.assertEqual(rule.destination_port_ranges, [])

    def test_switching_to_udp_clears_the_stored_tcp_flags(self):
        """Test that saving a TCP rule as UDP clears its stored TCP flags and resets their match mode to all."""
        rule = self._rule(
            10,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_SYN, ACLTCPFlagChoices.FLAG_ACK],
            tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
        )
        # The data still carries the flags and the match mode, as a stale page would.
        form = self._bound_form(
            instance=rule,
            protocol=ACLProtocolChoices.PROTOCOL_UDP,
            tcp_flags=[ACLTCPFlagChoices.FLAG_ACK],
            tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
        )
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        form.save()
        rule.refresh_from_db()
        self.assertEqual(rule.tcp_flags, [])
        self.assertEqual(rule.tcp_flags_match, ACLTCPFlagMatchChoices.MATCH_ALL)

    def test_switching_to_tcp_clears_the_stored_icmp_type_and_code(self):
        """Test that saving an ICMP rule as TCP clears its stored ICMP type and code."""
        rule = self._rule(10, protocol=ACLProtocolChoices.PROTOCOL_ICMP, icmp_type=8, icmp_code=0)
        # The data still carries the ICMP type and code, as a stale page would.
        form = self._bound_form(instance=rule, protocol=ACLProtocolChoices.PROTOCOL_TCP, icmp_type=8, icmp_code=0)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        form.save()
        rule.refresh_from_db()
        self.assertIsNone(rule.icmp_type)
        self.assertIsNone(rule.icmp_code)

    def test_stale_switch_to_icmp_reports_the_conflict(self):
        """Test that a stale form switching a TCP rule with ports to ICMP reports the conflict."""
        rule = self._rule(
            10,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            source_port_ranges=[NumericRange(22, 23)],
            destination_port_ranges=[NumericRange(443, 444)],
        )
        form = self._bound_form(instance=rule, protocol=ACLProtocolChoices.PROTOCOL_ICMP, _init_time="1")
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_switching_to_remark_clears_the_match_criteria(self):
        """Test that saving a rule as a remark clears every stored match criterion."""
        rule = self._rule(
            10,
            protocol=ACLProtocolChoices.PROTOCOL_TCP,
            source_port_ranges=[NumericRange(22, 23)],
            destination_port_ranges=[NumericRange(443, 444)],
            tcp_flags=[ACLTCPFlagChoices.FLAG_ACK],
            tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
            log_matches=True,
            log_options=[ACLRuleLogOptionChoices.OPTION_SYSLOG],
        )
        # The data still carries the protocol, both objects and the TCP flags, as a stale page would.
        form = self._bound_form(
            instance=rule,
            action=ACLRuleActionChoices.ACTION_REMARK,
            remark="Note",
            tcp_flags=[ACLTCPFlagChoices.FLAG_ACK],
            tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY,
        )
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

        form.save()
        rule.refresh_from_db()
        self.assertIsNone(rule.source_type)
        self.assertIsNone(rule.source_id)
        self.assertIsNone(rule.destination_type)
        self.assertIsNone(rule.destination_id)
        self.assertEqual(rule.protocol, "")
        self.assertEqual(rule.source_port_ranges, [])
        self.assertEqual(rule.destination_port_ranges, [])
        self.assertEqual(rule.tcp_flags, [])
        self.assertEqual(rule.tcp_flags_match, ACLTCPFlagMatchChoices.MATCH_ALL)
        self.assertFalse(rule.log_matches)
        self.assertEqual(rule.log_options, [])

    def test_action_and_protocol_redraw_the_form(self):
        """Test that changing the action or the protocol redraws the whole form."""
        form = ACLExtendedRuleForm(initial={"action": ACLRuleActionChoices.ACTION_PERMIT})
        for field_name in ("action", "protocol"):
            with self.subTest(field_name=field_name):
                attrs = form.fields[field_name].widget.attrs
                self.assertEqual(attrs["hx-get"], ".")
                self.assertEqual(attrs["hx-include"], "#form_fields")
                self.assertEqual(attrs["hx-target"], "#form_fields")

    def test_bulkedit_clear_empties_the_tcp_flags(self):
        """Test that the clear control empties the TCP flags."""
        form = ACLExtendedRuleBulkEditForm(
            data={"clear_tcp_flags": True, "pk": [self._rule(40).pk]},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["tcp_flags"], [])
        self.assertIn("tcp_flags", form.changed_data)

    def test_bulkedit_clear_rejects_an_explicit_tcp_flag_selection(self):
        """Test that clearing and selecting TCP flags at once is rejected."""
        form = ACLExtendedRuleBulkEditForm(
            data={
                "clear_tcp_flags": True,
                "tcp_flags": [ACLTCPFlagChoices.FLAG_ACK],
                "pk": [self._rule(50).pk],
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("clear_tcp_flags", form.errors)

    def test_bulkedit_blank_fields_leave_icmp_and_tcp_flags_unchanged(self):
        """Test that blank ICMP and TCP flag inputs stay out of the applied changes."""
        form = ACLExtendedRuleBulkEditForm(
            data={"description": "Bulk edited", "pk": [self._rule(60).pk]},
        )
        self.assertIn("icmp_type", form.fields)
        self.assertIn("icmp_code", form.fields)
        self.assertIn("tcp_flags", form.fields)
        self.assertIn("tcp_flags_match", form.fields)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn("icmp_type", form.changed_data)
        self.assertNotIn("icmp_code", form.changed_data)
        self.assertNotIn("tcp_flags", form.changed_data)
        self.assertNotIn("tcp_flags_match", form.changed_data)

    def test_bulkedit_applies_an_icmp_type_of_zero(self):
        """Test that an ICMP type of zero counts as a change."""
        form = ACLExtendedRuleBulkEditForm(
            data={"icmp_type": "0", "pk": [self._rule(70).pk]},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["icmp_type"], 0)
        self.assertIn("icmp_type", form.changed_data)

    def test_bulkedit_icmp_type_offers_the_family_labelled_presets(self):
        """Test that the bulk edit ICMP type offers the presets of both families."""
        form = ACLExtendedRuleBulkEditForm()
        self.assertIs(form.fields["icmp_type"].widget.options, ACLICMPTypeChoices)


class ACLExtendedRuleImportFormTestCase(TestCase):
    """
    Import form tests for ACLExtendedRule.

    Only what is extended-specific. The shared resolver's branches are covered once, against
    the standard rule, in ACLStandardRuleImportFormTestCase.
    """

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
        cls.standard_access_list = AccessList.objects.create(
            name="teststandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

    def _form(self, instance=None, **columns):
        """Build the form from the default row, with None removing a column."""
        data = {
            "access_list": self.access_list.name,
            "sequence": "10",
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "protocol": ACLProtocolChoices.PROTOCOL_TCP,
            "source_type": "ipam.prefix",
            "source": str(self.prefix.prefix),
            "destination_type": "ipam.ipaddress",
            "destination": str(self.ip_address.address),
        }
        data.update(columns)
        return ACLExtendedRuleImportForm(
            data={key: value for key, value in data.items() if value is not None},
            instance=instance,
        )

    def test_unknown_source_id_is_rejected(self):
        """Test that a source ID matching no object is rejected."""
        form = self._form(source=None, source_id=str(UNRESOLVABLE_OBJECT_ID))
        self.assertFalse(form.is_valid())
        self.assertIn("not found", str(form.errors["source_id"]))

    def test_unknown_destination_id_is_rejected(self):
        """Test that a destination ID matching no object is rejected."""
        form = self._form(destination=None, destination_id=str(UNRESOLVABLE_OBJECT_ID))
        self.assertFalse(form.is_valid())
        self.assertIn("not found", str(form.errors["destination_id"]))

    def test_both_roles_resolve_from_values(self):
        """object_roles runs the resolver twice, against two different content types."""
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        self.assertEqual(rule.source, self.prefix)
        self.assertEqual(rule.destination, self.ip_address)

    def test_address_group_roles_resolve_from_names(self):
        """Test that the address group values are looked up by the name field."""
        address_group = ACLAddressGroup.objects.create(name="address-group-1")
        form = self._form(
            source_type="netbox_acls.acladdressgroup",
            source=address_group.name,
            destination_type="netbox_acls.acladdressgroup",
            destination=address_group.name,
        )
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        self.assertEqual(rule.source, address_group)
        self.assertEqual(rule.destination, address_group)

    def test_standard_access_list_is_rejected(self):
        """The access list column offers extended lists only."""
        form = self._form(access_list=self.standard_access_list.name)
        self.assertFalse(form.is_valid())
        self.assertIn("access_list", form.errors)

    def test_a_shared_name_resolves_to_the_extended_list(self):
        """Access list names are not unique, so the column's queryset picks the extended one."""
        AccessList.objects.create(
            name=self.access_list.name,
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().access_list, self.access_list)

    def test_port_ranges_round_trip_in_the_inclusive_form(self):
        """Ports are stored half-open and read back inclusive, matching the detail view."""
        form = self._form(source_port_ranges="80-81,443")
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        self.assertEqual(
            [(r.lower, r.upper) for r in rule.source_port_ranges],
            [(80, 82), (443, 444)],
        )
        self.assertEqual(rule.source_port_ranges_list, ["80-81", "443"])

    def test_reversed_port_range_is_rejected(self):
        """A range whose end precedes its start is rejected."""
        form = self._form(source_port_ranges="443-80")
        self.assertFalse(form.is_valid())
        self.assertIn("source_port_ranges", form.errors)

    def test_overlapping_port_ranges_are_rejected(self):
        """Two ranges covering the same port are rejected."""
        form = self._form(source_port_ranges="80-100,90-110")
        self.assertFalse(form.is_valid())
        self.assertIn("overlap", str(form.errors))

    def test_ports_without_tcp_or_udp_are_rejected(self):
        """Port ranges need a protocol that has ports."""
        form = self._form(protocol=ACLProtocolChoices.PROTOCOL_IP, source_port_ranges="80")
        self.assertFalse(form.is_valid())
        self.assertIn("source_port_ranges", form.errors)

    def test_blank_destination_columns_clear_only_the_destination(self):
        """The two roles are independent, so clearing one leaves the other stored."""
        rule = self._form().save()

        form = ACLExtendedRuleImportForm(
            data={
                "access_list": self.access_list.name,
                "sequence": "10",
                "action": rule.action,
                "protocol": rule.protocol,
                "source_type": "ipam.prefix",
                "source": str(self.prefix.prefix),
                "destination_type": "",
                "destination": "",
                "destination_id": "",
            },
            instance=rule,
        )

        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertIsNone(updated.destination)
        self.assertEqual(updated.source, self.prefix)

    def test_icmp_type_and_code_of_zero_are_imported(self):
        """Test that an ICMP type and code of zero import as zero."""
        form = self._form(protocol=ACLProtocolChoices.PROTOCOL_ICMP, icmp_type="0", icmp_code="0")
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        self.assertEqual((rule.icmp_type, rule.icmp_code), (0, 0))

    def test_blank_tcp_flags_match_cell_keeps_the_default(self):
        """Test that a blank TCP flags match cell imports the default."""
        form = self._form(tcp_flags_match="")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().tcp_flags_match, ACLTCPFlagMatchChoices.MATCH_ALL)

    def test_blank_tcp_flags_match_cell_keeps_the_stored_match(self):
        """Test that a blank TCP flags match cell keeps the stored match on update."""
        rule = self._form(tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY).save()
        form = self._form(instance=rule, tcp_flags_match="")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().tcp_flags_match, ACLTCPFlagMatchChoices.MATCH_ANY)

    def test_tcp_flags_are_imported_canonically(self):
        """Test that imported TCP flags deduplicate and reach the database in header-bit order."""
        form = self._form(tcp_flags="ack,syn,ack", tcp_flags_match=ACLTCPFlagMatchChoices.MATCH_ANY)
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        rule.refresh_from_db()
        self.assertEqual(rule.tcp_flags, [ACLTCPFlagChoices.FLAG_SYN, ACLTCPFlagChoices.FLAG_ACK])
        self.assertEqual(rule.tcp_flags_match, ACLTCPFlagMatchChoices.MATCH_ANY)

    def test_update_changing_protocol_with_an_omitted_tcp_flags_column_is_rejected(self):
        """Test that an update leaving TCP flags on a UDP rule reports a row error."""
        rule = self._form(tcp_flags=ACLTCPFlagChoices.FLAG_ACK).save()

        form = ACLExtendedRuleImportForm(data={"protocol": ACLProtocolChoices.PROTOCOL_UDP}, instance=rule)
        # BulkImportView deletes every field the record omits.
        for name in set(form.fields) - {"protocol"}:
            del form.fields[name]

        self.assertFalse(form.is_valid())
        self.assertIn(
            "tcp_flags: TCP Flags can only be set when the protocol is TCP.",
            form.non_field_errors(),
        )
