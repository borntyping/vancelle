from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, fragment
from vancelle.models import Entry


def EntryAlreadyExistsFlash(entry: Entry) -> Heavymetal:
    return fragment([a({"href": entry.url_for()}, [entry.title]), " is already attached to a work."])
