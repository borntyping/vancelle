from vancelle.lib.heavymetal.html import br, fragment, make_element

invalid = make_element("invalid")


def test_make_element():
    br = make_element("br")

    assert br({}, []) == ("br", {}, [])


def test_make_element_metadata():
    assert invalid.__name__ == "invalid"
    assert "<locals>" not in invalid.__qualname__


def test_fragment():
    document = fragment([br({})])

    assert document == (None, {}, [("br", {}, [])])
