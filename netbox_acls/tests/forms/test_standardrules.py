from django import forms
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Prefix

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ...constants import ACL_RULE_OBJECT_LOOKUPS, ACL_RULE_SOURCE_DESTINATION_MODELS
from ...forms import (
    ACLStandardRuleBulkEditForm,
    ACLStandardRuleFilterForm,
    ACLStandardRuleForm,
    ACLStandardRuleImportForm,
)
from ...models import AccessList, ACLStandardRule
from ..views.base import build_ipam_objects
from .base import BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin

UNRESOLVABLE_OBJECT_ID = 99999999


class ACLStandardRuleFormTestCase(BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin, TestCase):
    """Form tests for ACLStandardRule forms."""

    bulk_edit_form = ACLStandardRuleBulkEditForm
    filter_form = ACLStandardRuleFilterForm

    @classmethod
    def setUpTestData(cls):
        cls.aggregate, cls.prefix, cls.ip_address, cls.ip_range = build_ipam_objects()
        cls.access_list = AccessList.objects.create(
            name="teststandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

    def _bound_form(self, source):
        """Bind the form, so the posted source type reaches __init__."""
        return ACLStandardRuleForm(
            data={
                "access_list": self.access_list.pk,
                "sequence": 10,
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_content_type": ContentType.objects.get_for_model(source).pk,
                "source_object_id": source.pk,
            },
        )

    def _rule(self, sequence):
        return ACLStandardRule.objects.create(
            access_list=self.access_list,
            sequence=sequence,
            action=ACLRuleActionChoices.ACTION_PERMIT,
            source=self.prefix,
        )

    def test_instance_seeds_the_source_field(self):
        """An existing rule's source reaches the form as its initial value."""
        form = ACLStandardRuleForm(instance=self._rule(10))
        self.assertEqual(form.initial["source"], self.prefix)

    def test_source_queryset_follows_the_posted_type(self):
        """Test that switching type while editing re-scopes the object picker."""
        rule = self._rule(20)
        form = ACLStandardRuleForm(
            data={
                "access_list": self.access_list.pk,
                "sequence": 20,
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_content_type": ContentType.objects.get_for_model(self.ip_address).pk,
            },
            instance=rule,
        )
        field = form.fields["source"]
        self.assertIs(field.selected_model, type(self.ip_address))
        self.assertEqual(field.queryset.model, type(self.ip_address))

    def test_editing_rejects_a_type_change_that_names_no_object(self):
        """Test that switching type without picking an object fails validation."""
        # Values arrive as text, the way a browser posts them.
        rule = self._rule(25)
        form = ACLStandardRuleForm(
            data={
                "access_list": str(self.access_list.pk),
                "sequence": "25",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_content_type": str(ContentType.objects.get_for_model(self.ip_address).pk),
            },
            instance=rule,
        )
        # A type with no object is a validation error rather than a silent clear.
        self.assertFalse(form.is_valid())
        self.assertIn("source", form.errors)

    def test_editing_keeps_the_source_when_the_type_is_unchanged(self):
        """Test that an edit holds on to the selected source when its type did not change."""
        # Values arrive as text, the way a browser posts them.
        rule = self._rule(30)
        form = ACLStandardRuleForm(
            data={
                "access_list": str(self.access_list.pk),
                "sequence": "30",
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_content_type": str(ContentType.objects.get_for_model(self.prefix).pk),
                "source_object_id": str(self.prefix.pk),
            },
            instance=rule,
        )
        self.assertIs(form.fields["source"].selected_model, type(self.prefix))
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertEqual(form.instance.source, self.prefix)

    def test_bulkedit_access_list_filtered_to_standard(self):
        """Guard the standard bulk-edit picker the extended form (#360) was copied from."""
        form = ACLStandardRuleBulkEditForm()
        self.assertEqual(
            form.fields["access_list"].query_params,
            {"type": ACLTypeChoices.TYPE_STANDARD},
        )

    def test_access_list_queryset_limited_to_standard(self):
        """Test that the model form's Access List picker filters to Standard ACLs."""
        form = ACLStandardRuleForm()
        self.assertEqual(
            form.fields["access_list"].query_params,
            {"type": ACLTypeChoices.TYPE_STANDARD},
        )

    def test_source_queryset_follows_type(self):
        """Test that the source picker's queryset is resolved from the posted source type."""
        for source in (self.aggregate, self.prefix, self.ip_address, self.ip_range):
            with self.subTest(source=source._meta.label_lower):
                form = self._bound_form(source)
                field = form.fields["source"]
                self.assertIs(field.selected_model, type(source))
                self.assertEqual(field.queryset.model, type(source))

    def test_source_type_choices_limited(self):
        """Test that the source type picker offers only the ipam models a rule accepts."""
        form = ACLStandardRuleForm()
        self.assertQuerySetEqual(
            form.fields["source"].content_type_field.queryset.order_by("pk"),
            ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS).order_by("pk"),
            transform=lambda ct: ct,
        )

    def test_clean_assigns_source(self):
        """Test that a valid form assigns the selected source to the instance."""
        form = self._bound_form(self.prefix)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        self.assertEqual(form.instance.source, self.prefix)

    def test_bulkedit_source_queryset_follows_type(self):
        """Test that the bulk-edit source picker's queryset is resolved from the posted type."""
        form = ACLStandardRuleBulkEditForm(
            data={"source_content_type": ContentType.objects.get_for_model(type(self.prefix)).pk},
        )
        self.assertIs(form.fields["source"].selected_model, type(self.prefix))
        self.assertEqual(form.fields["source"].queryset.model, type(self.prefix))

    def test_bulkedit_source_type_widget_swaps_the_form_fields(self):
        """Test that the bulk-edit type picker posts and swaps, unlike the model form's picker."""
        attrs = ACLStandardRuleBulkEditForm().fields["source"].content_type_field.widget.attrs
        self.assertEqual(attrs["hx-post"], ".")
        self.assertEqual(attrs["hx-select"], "#form_fields")

    def test_bulkedit_source_label_names_the_role(self):
        """Test that the label names the role, since the type picker sits inside the field."""
        form = ACLStandardRuleBulkEditForm(
            data={"source_content_type": ContentType.objects.get_for_model(self.ip_range).pk},
        )
        self.assertEqual(form.fields["source"].label, "Source")

    def test_bulkedit_nullable_fields(self):
        """Test that the nullable list stays exhaustive for this form."""
        self.assertEqual(
            ACLStandardRuleBulkEditForm.nullable_fields,
            ("remark", "source", "description", "comments"),
        )

    def test_filterform_carries_no_extended_filters(self):
        """Test that the shared mixin leaks no extended-only filter into the standard form."""
        form = ACLStandardRuleFilterForm()
        for name in ("protocol", "source_port", "destination_port"):
            self.assertNotIn(name, form.fields)
        for model_name in ("aggregate", "ipaddress", "iprange", "prefix"):
            self.assertNotIn(f"destination_{model_name}_id", form.fields)

    def test_filterform_access_list_filtered_to_standard(self):
        """Test that the filter form's Access List picker filters to Standard ACLs."""
        form = ACLStandardRuleFilterForm()
        self.assertEqual(
            form.fields["access_list_id"].query_params,
            {"type": ACLTypeChoices.TYPE_STANDARD},
        )

    def test_logging_fields_are_present(self):
        """Test that the model form exposes both logging fields."""
        form = ACLStandardRuleForm()
        self.assertIn("log_matches", form.fields)
        self.assertIn("log_options", form.fields)

    def test_log_options_group_vendor_specific_choices(self):
        """Test that a vendor-specific option is offered under its vendor's group."""
        form = ACLStandardRuleForm()
        groups = {
            group: [value for value, _label in options]
            for group, options in form.fields["log_options"].choices
            if isinstance(options, (list, tuple))
        }
        self.assertEqual(
            groups["Cisco"],
            [ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT],
        )

    def test_form_rejects_options_without_log_matches(self):
        """Test that the model form surfaces the consistency error per field."""
        form = ACLStandardRuleForm(
            data={
                "access_list": self.access_list.pk,
                "sequence": 10,
                "action": ACLRuleActionChoices.ACTION_PERMIT,
                "source_type": ContentType.objects.get_for_model(type(self.prefix)).pk,
                "source": self.prefix.pk,
                "log_options": [ACLRuleLogOptionChoices.OPTION_SYSLOG],
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("log_options", form.errors)

    def test_bulkedit_disabling_logging_clears_the_options(self):
        """Test that turning logging off also drops the options."""
        form = ACLStandardRuleBulkEditForm(
            data={"log_matches": "False", "pk": [self._rule(10).pk]},
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["log_options"], [])
        self.assertIn("log_options", form.changed_data)

    def test_bulkedit_clear_rejects_an_explicit_selection(self):
        """Test that clearing and selecting log options at once is rejected."""
        form = ACLStandardRuleBulkEditForm(
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
        form = ACLStandardRuleBulkEditForm(
            data={
                "log_matches": "False",
                "log_options": [ACLRuleLogOptionChoices.OPTION_SYSLOG],
                "pk": [self._rule(30).pk],
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("log_options", form.errors)

    def test_choice_filters_accept_multiple_values(self):
        """The filter form's action field must be a multi-select, matching the filter set."""
        form = ACLStandardRuleFilterForm()
        self.assertIsInstance(form.fields["action"], forms.MultipleChoiceField)


class ACLRuleObjectLookupTestCase(TestCase):
    """Guard the import lookup map against the content type filter drifting away from it."""

    def test_lookup_map_covers_every_source_or_destination_type(self):
        """Test that the map names exactly the types the content type filter selects."""
        selected = {
            f"{object_type.app_label}.{object_type.model}"
            for object_type in ContentType.objects.filter(ACL_RULE_SOURCE_DESTINATION_MODELS)
        }

        self.assertEqual(selected, set(ACL_RULE_OBJECT_LOOKUPS))


class ACLStandardRuleImportFormTestCase(TestCase):
    """Import form tests for ACLStandardRule."""

    @classmethod
    def setUpTestData(cls):
        cls.aggregate, cls.prefix, cls.ip_address, cls.ip_range = build_ipam_objects()
        cls.ipv6_prefix = Prefix.objects.create(prefix=IPNetwork("2001:db8::/32"))

        cls.access_list = AccessList.objects.create(
            name="teststandardacl",
            type=ACLTypeChoices.TYPE_STANDARD,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )
        cls.extended_access_list = AccessList.objects.create(
            name="testextendedacl",
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

    def _form(self, instance=None, **columns):
        """Build the form from the default row, with None removing a column."""
        data = {
            "access_list": self.access_list.name,
            "sequence": "10",
            "action": ACLRuleActionChoices.ACTION_PERMIT,
            "source_type": "ipam.prefix",
            "source": str(self.prefix.prefix),
        }
        data.update(columns)
        return ACLStandardRuleImportForm(
            data={key: value for key, value in data.items() if value is not None},
            instance=instance,
        )

    def test_prefix_source_resolves(self):
        """The prefix value is looked up by the prefix field, per ACL_RULE_OBJECT_LOOKUPS."""
        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().source, self.prefix)

    def test_address_source_resolves(self):
        """The address value is looked up by the address field, not by prefix."""
        form = self._form(source_type="ipam.ipaddress", source=str(self.ip_address.address))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().source, self.ip_address)

    def test_aggregate_source_resolves(self):
        """The aggregate value is looked up by the prefix field, which it shares with Prefix."""
        form = self._form(source_type="ipam.aggregate", source=str(self.aggregate.prefix))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().source, self.aggregate)

    def test_ip_range_value_is_rejected(self):
        """Test that an IP range has no value form and the error names the ID column."""
        form = self._form(source_type="ipam.iprange", source="10.0.1.1-10.0.1.254")
        self.assertFalse(form.is_valid())
        self.assertIn("source_id", str(form.errors["source"]))

    def test_ip_range_resolves_by_id(self):
        """Test that an IP range resolves from its numeric ID."""
        form = self._form(source_type="ipam.iprange", source=None, source_id=str(self.ip_range.pk))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().source, self.ip_range)

    def test_unknown_source_id_is_rejected(self):
        """Test that a source ID matching no object is rejected."""
        form = self._form(source=None, source_id=str(UNRESOLVABLE_OBJECT_ID))
        self.assertFalse(form.is_valid())
        self.assertIn("not found", str(form.errors["source_id"]))

    def test_extended_access_list_is_rejected(self):
        """Test that an extended list is rejected, which ForeignKey.validate enforces."""
        form = self._form(access_list=self.extended_access_list.name)
        self.assertFalse(form.is_valid())
        self.assertIn("access_list", form.errors)

    def test_a_shared_name_resolves_to_the_standard_list(self):
        """Access list names are not unique, so the column's queryset picks the standard one."""
        shared = AccessList.objects.create(
            name=self.access_list.name,
            type=ACLTypeChoices.TYPE_EXTENDED,
            family=ACLFamilyChoices.FAMILY_IPV4,
            default_action=ACLActionChoices.ACTION_DENY,
        )

        form = self._form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().access_list, self.access_list)
        self.assertNotEqual(form.instance.access_list, shared)

    def test_unknown_access_list_is_reported_not_raised(self):
        """Test that an unresolvable access list name is a field error, not an exception."""
        form = self._form(access_list="no-such-acl", source=None, source_type=None)
        self.assertFalse(form.is_valid())
        self.assertIn("access_list", form.errors)

    def test_remark_with_a_source_is_rejected(self):
        """Test that the model's remark rule fires through the import form."""
        form = self._form(action=ACLRuleActionChoices.ACTION_REMARK, remark="a remark")
        self.assertFalse(form.is_valid())
        self.assertIn("source", form.errors)

    def test_remark_without_a_remark_is_rejected(self):
        """Test that a remark rule needs remark text."""
        form = self._form(action=ACLRuleActionChoices.ACTION_REMARK, source=None, source_type=None)
        self.assertFalse(form.is_valid())
        self.assertIn("remark", form.errors)

    def test_duplicate_sequence_is_rejected(self):
        """Test that two rules cannot share a sequence on one access list."""
        self._form().save()

        form = self._form(source_type="ipam.ipaddress", source=str(self.ip_address.address))
        self.assertFalse(form.is_valid())
        self.assertIn("sequence", str(form.errors))

    def test_ipv6_source_on_an_ipv4_access_list_is_rejected(self):
        """Test that the family guard fires through the import form."""
        form = self._form(source=str(self.ipv6_prefix.prefix))
        self.assertFalse(form.is_valid())
        self.assertIn("IPv6 criteria", str(form.errors))

    def test_log_options_without_log_matches_is_rejected(self):
        """Test that log options need log matches."""
        form = self._form(log_options=ACLRuleLogOptionChoices.OPTION_SYSLOG)
        self.assertFalse(form.is_valid())
        self.assertIn("log_options", form.errors)

    def test_log_options_accepts_a_comma_string(self):
        """Test that a comma separated cell stores every option."""
        form = self._form(
            log_matches="true",
            log_options=f"{ACLRuleLogOptionChoices.OPTION_SYSLOG},{ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT}",
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertCountEqual(
            form.save().log_options,
            [ACLRuleLogOptionChoices.OPTION_SYSLOG, ACLRuleLogOptionChoices.OPTION_CISCO_LOG_INPUT],
        )

    def test_update_without_source_columns_keeps_the_source(self):
        """Test that an update omitting every source column preserves the stored source."""
        rule = self._form().save()

        form = ACLStandardRuleImportForm(data={"description": "updated"}, instance=rule)
        # BulkImportView deletes every field the record omits.
        for name in ("access_list", "sequence", "action", "source_type", "source", "source_id"):
            del form.fields[name]

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().source, self.prefix)

    def test_update_with_blank_source_columns_clears_the_source(self):
        """Test that blank source columns clear the stored source."""
        rule = self._form().save()

        form = ACLStandardRuleImportForm(
            data={
                "access_list": self.access_list.name,
                "sequence": "10",
                "action": rule.action,
                "source_type": "",
                "source": "",
                "source_id": "",
            },
            instance=rule,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.save().source)

    def test_update_with_a_type_and_no_object_reports_a_field_error(self):
        """An update row naming a type but no object must be a field error, not an exception."""
        rule = self._form().save()

        form = ACLStandardRuleImportForm(
            data={"source_type": "ipam.prefix", "source_id": ""},
            instance=rule,
        )
        # BulkImportView deletes every field the record omits.
        for name in ("access_list", "sequence", "action", "remark", "source"):
            del form.fields[name]

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)
