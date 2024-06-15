from vancelle.lib.heavymetal.html import br, fragment, make_element, nothing

invalid = make_element("invalid")


def test_make_element():
    element = make_element("br")

    assert element({}, []) == ("br", {}, [])


def test_make_element_metadata():
    assert invalid.__name__ == "invalid"
    assert "<locals>" not in invalid.__qualname__


def test_fragment():
    document = fragment([br({})])

    assert document == (None, {}, [("br", {}, [])])


def test_nothing():
    document = nothing()

    assert document == (None, {}, ())
