from .helpers import merge_attrs


def test_merge_attrs():
    assert merge_attrs({"class": "row"}, {"class": "col"}) == {"class": "row col"}


# @pytest.mark.xfail()
# def test_merge_attrs_duplicate():
#     with pytest.raises(Exception):
#         merge_attrs({"data-x": "a"}, {"data-x": "b"})
