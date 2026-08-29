from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from ...choices import (
    ACLActionChoices,
    ACLFamilyChoices,
    ACLRuleActionChoices,
    ACLRuleLogOptionChoices,
    ACLTypeChoices,
)
from ...constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from ...forms import ACLStandardRuleBulkEditForm, ACLStandardRuleFilterForm, ACLStandardRuleForm
from ...models import AccessList, ACLStandardRule
from ..views.base import build_ipam_objects
from .base import BulkEditFieldsetTestMixin, FilterFormFieldsetTestMixin


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

    def test_changing_the_source_type_clears_the_source(self):
        """Switching type while editing drops the object the old type selected."""
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
        self.assertFalse(field.object_field.queryset.exists())

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
            data={"source_type": ContentType.objects.get_for_model(type(self.prefix)).pk},
        )
        self.assertEqual(form.fields["source"].queryset.model, type(self.prefix))
        self.assertFalse(form.fields["source"].disabled)

    def test_bulkedit_source_type_widget_swaps_the_form_fields(self):
        """Test that the bulk-edit type picker posts and swaps, unlike the model form's picker."""
        attrs = ACLStandardRuleBulkEditForm().fields["source_type"].widget.attrs
        self.assertEqual(attrs["hx-post"], ".")
        self.assertEqual(attrs["hx-select"], "#form_fields")

    def test_bulkedit_source_label_follows_type(self):
        """Test that the resolved label names the role and the selected model."""
        form = ACLStandardRuleBulkEditForm(
            data={"source_type": ContentType.objects.get_for_model(self.ip_range).pk},
        )
        self.assertEqual(form.fields["source"].label, "Source IP Range")

    def test_bulkedit_nullable_fields(self):
        """Test that the nullable list stays exhaustive for this form."""
        self.assertEqual(
            ACLStandardRuleBulkEditForm.nullable_fields,
            ("remark", "source_type", "source", "description", "comments"),
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
