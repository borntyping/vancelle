import typing

Size = typing.Literal["S", "M", "L"]
KeyType = typing.Literal["ISBN", "OCLC", "LCCN", "OLID", "ID"]


class Reference(typing.TypedDict):
    key: str


class SearchDoc(typing.TypedDict):
    key: str  # example: "/works/OL20861787W"
    type: typing.Literal["work"]
    title: str
    title_suggest: str
    title_sort: str
    edition_count: int
    edition_key: list[str]
    publish_date: list[str]
    publish_year: list[str]
    first_publish_year: str
    number_of_pages_median: int
    publish_place: list[str]
    isbn: list[str]
    cover_edition_key: typing.NotRequired[str]
    first_sentence: list[str]
    language: list[str]
    author_key: list[str]
    author_name: list[str]
    id_goodreads: typing.NotRequired[list[str]]

    cover_i: int


class Search(typing.TypedDict):
    numFound: int
    numFoundExact: bool
    start: int

    docs: list[SearchDoc]


class WorkDescription(typing.TypedDict):
    type: typing.Literal["/type/text"]
    value: str


class AuthorReference(typing.TypedDict):
    author: Reference
    key: Reference


class Work(typing.TypedDict):
    title: str
    covers: list[int]
    key: str  # "/works/{openlibrary_id}"
    authors: list[AuthorReference]
    type: Reference
    subjects: list[str]
    description: WorkDescription
    latest_revision: int
    revision: int
    created: dict  # { type: str = '/type/datetime', value: str }
    last_modified: dict  # { type: str = '/type/datetime', value: str }


"""
Table of contents entry.
Has a field named 'class' so has to use the alternate TypedDict format.
https://openlibrary.org/type/toc_item
"""
TocItem = typing.TypedDict("TocItem", {"class": str, "label": str, "title": str, "pagenum": str})


class EditionIdentifiers(typing.TypedDict):
    goodreads: list[str]
    librarything: list[str]


class Edition(typing.TypedDict):
    """
    Schema used in both the Works API and the Editions API.
    The same data isn't guaranteed to appear in both.

    https://openlibrary.org/type/edition
    https://openlibrary.org/works/OL20861787W/editions.json
    https://openlibrary.org/books/OL32043957M.json
    """

    key: str
    type: Reference
    identifiers: EditionIdentifiers
    covers: list[int]  # Undocumented.  Might be a backref?

    # From https://openlibrary.org/type/edition
    title: str
    title_prefix: typing.NotRequired[str]
    subtitle: typing.NotRequired[str]
    other_titles: typing.NotRequired[list[str]]
    authors: list[Reference]
    publish_date: str
    copyright_date: str
    edition_name: str
    languages: list[Reference]
    description: str
    notes: str
    genres: list[str]
    table_of_contents: list[TocItem]
    work_titles: list[str]
    series: list[str]
    physical_dimensions: str
    physical_format: str
    number_of_pages: int
    subjects: list[str]
    pagination: str
    lccn: list[str]
    ocaid: str
    oclc_numbers: list[str]
    isbn_10: list[str]
    isbn_13: list[str]
    dewey_decimal_class: list[str]
    lc_classifications: list[str]
    contributions: list[str]
    publish_places: list[str]
    publish_country: str
    publishers: list[str]
    distributors: list[str]
    first_sentence: str
    weight: str
    location: list[str]
    scan_on_demand: bool
    collections: list
    uris: list[str]
    uri_descriptions: list[str]
    translation_of: str
    works: list[Reference]
    source_records: list[str]
    translated_from: list[Reference]
    scan_records: list[Reference]
    volumes: list[Reference]
    accompanying_material: str


class WorkEditions(typing.TypedDict):
    links: dict  # { self: str, work: str = '/works/{id}' }
    size: int
    entries: list[Edition]


class AuthorLink(typing.TypedDict):
    url: str
    title: str
    type: Reference  # "/type/link"


class Author(typing.TypedDict):
    """
    https://openlibrary.org/authors/OL1425963A.json
    """

    remote_ids: dict
    photos: list[int]
    key: str
    personal_name: str
    birth_date: str
    source_records: list[str]
    name: str
    type: Reference  # "/type/author"
    links: list[AuthorLink]
    bio: str
    latest_revision: int
    revision: int
    created: dict  # { type: str = '/type/datetime', value: str }
    last_modified: dict  # { type: str = '/type/datetime', value: str }
