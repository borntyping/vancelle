import typing

GoodreadsCsvRow = typing.TypedDict(
    "GoodreadsCsvRow",
    {
        "Book Id": str,
        "Title": str,
        "Author": str,
        "Author l-f": str,
        "Additional Authors": str,
        "ISBN": str,
        "ISBN13": str,
        "My Rating": str,
        "Average Rating": str,
        "Publisher": str,
        "Binding": str,
        "Number of Pages": str,
        "Year Published": str,
        "Original Publication Year": str,
        "Date Read": str,
        "Date Added": str,
        "Bookshelves": str,
        "Bookshelves with positions": str,
        "Exclusive Shelf": str,
        "My Review": str,
        "Spoiler": str,
        "Private Notes": str,
        "Read Count": str,
        "Owned Copies": str,
    },
)

GoodreadsHtmlRow = typing.TypedDict(
    "GoodreadsHtmlRow",
    {
        "asin": str,
    },
)
