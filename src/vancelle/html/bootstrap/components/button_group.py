from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent


def btn_group(buttons: HeavymetalContent, tag: str = "div") -> Heavymetal:
    return (tag, {"class": "btn-group"}, buttons)


def btn_toolbar(groups: HeavymetalContent, tag: str = "div") -> Heavymetal:
    return (tag, {"class": "btn-toolbar"}, groups)
