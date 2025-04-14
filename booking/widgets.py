# widgets.py
import json

from django import forms
from django.utils.safestring import mark_safe


class HierarchicalNamesJSONWidget(forms.Textarea):
    def format_json(self, json_data, indent=0):
        html = ""
        if isinstance(json_data, dict):
            if 'name' in json_data:
                html += f"<li>{json_data['name']}</li>"
            for key, value in json_data.items():
                if isinstance(value, (dict, list)):
                    html += self.format_json(value, indent + 2)
        elif isinstance(json_data, list):
            html += "<ul>"
            for item in json_data:
                html += self.format_json(item, indent + 2)
            html += "</ul>"
        return html

    def format_value(self, value):
        if value is None:
            return ''
        try:
            json_data = json.loads(value)
            return self.format_json(json_data)
        except (TypeError, ValueError):
            return value

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        output = [
            f'<div style="border:1px solid #ccc; padding: 10px; max-height: 300px; overflow:auto;">{self.format_value(value)}</div>']
        return mark_safe('\n'.join(output))
