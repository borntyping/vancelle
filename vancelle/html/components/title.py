from vancelle.html.hotmetal import Hotmetal, element


def title(*parts: str) -> Hotmetal:
    return element("title", {}, [" - ".join(["Vancelle", *parts])])
