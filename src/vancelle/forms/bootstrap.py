import markupsafe
import wtforms

from vancelle.html.bootstrap.forms.controls import form_control


class BootstrapMeta:
    def render_field(self, field: wtforms.Field, kwargs) -> markupsafe.Markup:
        return form_control(field, **kwargs)
