import markupsafe
import wtforms
import wtforms.widgets


class MixedSelect(wtforms.widgets.Select):
    """A select field that can mix <option> and <optgroup>"""

    def __call__(self, field: wtforms.SelectFieldBase, **kwargs) -> markupsafe.Markup:
        kwargs.setdefault("id", field.id)
        if self.multiple:
            raise NotImplementedError
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        if not field.has_groups():
            raise NotImplementedError

        html = ["<select %s>" % wtforms.widgets.html_params(name=field.name, **kwargs)]

        if field.has_groups():
            for group, choices in field.iter_groups():
                options = [self.render_option(val, label, selected, **render_kw) for val, label, selected, render_kw in choices]

                if group:
                    html.append("<optgroup %s>" % wtforms.widgets.html_params(label=group))
                    html.extend(options)
                    html.append("</optgroup>")
                else:
                    html.extend(options)

        html.append("</select>")
        return markupsafe.Markup("".join(html))
