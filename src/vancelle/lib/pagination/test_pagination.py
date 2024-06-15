from . import Pagination


class TestPagination:
    def test_iter_page_first(self) -> None:
        pagination = Pagination(items=list(range(10)), count=90, page=1)
        pages = list(pagination.iter_page())
        assert pages == [1, 2, 3, None, 8, 9]

    def test_iter_page_last(self) -> None:
        pagination = Pagination(items=list(range(10)), count=90, page=9)
        pages = list(pagination.iter_page())
        assert pages == [1, 2, None, 7, 8, 9]

    def test_iter_page_breaks(self) -> None:
        pagination = Pagination(items=list(range(10)), count=200, page=10)
        pages = list(pagination.iter_page())
        assert pages == [1, 2, None, 8, 9, 10, 11, 12, None, 19, 20]

    def test_iter_pages_no_breaks(self) -> None:
        pagination = Pagination(items=list(range(10)), count=90, page=5)
        pages = list(pagination.iter_page())
        assert pages == [1, 2, 3, 4, 5, 6, 7, 8, 9]
