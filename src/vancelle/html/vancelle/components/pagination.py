from vancelle.ext.flask import url_with
from vancelle.html.bootstrap.components.pagination import PageItem, Pagination as BootstrapPagination
from vancelle.lib.pagination import Pagination


def nav_pagination(pagination: Pagination) -> BootstrapPagination:
    previous_page = PageItem("Previous", url_with(page=pagination.prev_page) if pagination.prev_page else None)
    pages = [
        (
            PageItem(str(page), url_with(page=page), active=(page == pagination.page))
            if page
            else PageItem("...", href=url_with(page=None))
        )
        for page in pagination.iter_page()
    ]
    next_page = PageItem("Next", url_with(page=pagination.next_page) if pagination.next_page else None)

    return BootstrapPagination([previous_page, *pages, next_page], center=True)
