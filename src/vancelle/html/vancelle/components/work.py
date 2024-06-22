from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, em
from vancelle.models import Work


def return_to_work(work: Work) -> Heavymetal:
    title = work.resolve_title()
    return a({"href": work.url_for()}, ["Return to ", em({}, [title])])
