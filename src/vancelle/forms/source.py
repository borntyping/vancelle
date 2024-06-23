import wtforms.validators

from vancelle.forms.bootstrap import BootstrapMeta
from vancelle.forms.pagination import PaginationArgs


class SourceSearchArgs(PaginationArgs):
    class Meta(BootstrapMeta):
        csrf = False

    search = wtforms.SearchField(label="Search", validators=[wtforms.validators.Optional()])
