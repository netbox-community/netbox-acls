"""
Define the custom table columns used by the plugin's tables.
"""

import django_tables2 as tables
from django.utils.html import format_html

from netbox.tables import columns

from ..choices import ACLRuleUsageChoices

__all__ = (
    "LogOptionsColumn",
    "UsedAsColumn",
)


class LogOptionsColumn(columns.TemplateColumn):
    """
    Display each log option as a colored badge.
    """

    template_code = """
    {% for label, color in record.log_options_badges %}
      {% badge label bg_color=color %}
    {% empty %}
      {{ ''|placeholder }}
    {% endfor %}
    """

    def __init__(self, **kwargs):
        super().__init__(template_code=self.template_code, orderable=False, **kwargs)

    def value(self, value):
        """Export the labels rather than the rendered badges."""
        return ", ".join(value)


class UsedAsColumn(tables.Column):
    """
    Display which end of an extended rule references the viewed object.
    """

    labels = dict(ACLRuleUsageChoices)

    def render(self, value):
        return format_html(
            '<span class="badge text-bg-{}">{}</span>',
            ACLRuleUsageChoices.colors.get(value, "secondary"),
            self.labels.get(value, value),
        )

    def value(self, value):
        """Export the label rather than the rendered badge."""
        return self.labels.get(value, value)
