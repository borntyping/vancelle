from vancelle.ext.flask import url_with
from vancelle.ext.flask_sqlalchemy import Pagination as SQLAlchemyPagination
from vancelle.html.bootstrap.components.pagination import Pagination as BootstrapPagination, PageItem


def nav_pagination(pagination: SQLAlchemyPagination) -> BootstrapPagination:
    previous_page = PageItem("Previous", url_with(page=pagination.prev_num) if pagination.has_prev else None)
    pages = [
        (
            PageItem(str(page), url_with(page=page), active=(page == pagination.page))
            if page
            else PageItem("...", href=url_with(page=None))
        )
        for page in pagination.iter_pages(left_edge=2, left_current=2, right_current=2, right_edge=2)
    ]
    next_page = PageItem("Next", url_with(page=pagination.next_num) if pagination.has_next else None)

    return BootstrapPagination([previous_page, *pages, next_page], center=True)
