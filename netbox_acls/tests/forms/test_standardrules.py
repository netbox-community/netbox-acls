from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from ...choices import ACLActionChoices, ACLFamilyChoices, ACLRuleActionChoices, ACLTypeChoices
from ...constants import ACL_RULE_SOURCE_DESTINATION_MODELS
from ...forms import ACLStandardRuleBulkEditForm, ACLStandardRuleForm
from ...models import AccessList
from ..views.base import build_ipam_objects
from .base import BulkEditFieldsetTestMixin


class ACLStandardRuleFormTestCase(BulkEditFieldsetTestMixin, TestCase):
    """Form tests for ACLStandardRule forms."""

    bulk_edit_form = ACLStandardRuleBulkEditForm

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
                "source_type": ContentType.objects.get_for_model(source).pk,
                "source": source.pk,
            },
        )

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
                self.assertEqual(form.fields["source"].queryset.model, type(source))
                self.assertFalse(form.fields["source"].disabled)

    def test_source_type_choices_limited(self):
        """Test that the source type picker offers only the ipam models a rule accepts."""
        form = ACLStandardRuleForm()
        self.assertQuerySetEqual(
            form.fields["source_type"].queryset.order_by("pk"),
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
