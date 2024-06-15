import sqlalchemy

from ..shelf import Shelf

ShelfEnum = sqlalchemy.Enum(Shelf, native_enum=False, validate_strings=True, values_callable=lambda e: [x.value for x in e])
