import typing

import sqlalchemy.dialects.postgresql
import sqlalchemy.ext.compiler
import sqlalchemy.orm
import sqlalchemy.orm.mapper
import sqlalchemy.sql.elements
import sqlalchemy.types
import structlog

logger = structlog.get_logger(logger_name=__name__)


def instance_to_dict(instance: sqlalchemy.orm.DeclarativeBase) -> dict:
    return {attr.key: getattr(instance, attr.key) for attr in sqlalchemy.inspect(instance.__class__).column_attrs}


def upsert(
    table: typing.Type[sqlalchemy.orm.DeclarativeBase],
    instances: sqlalchemy.orm.DeclarativeBase | typing.Sequence[sqlalchemy.orm.DeclarativeBase] = (),
) -> sqlalchemy.dialects.postgresql.Insert:
    """
    Perform an INSERT ... ON CONFLICT ... DO UPDATE query, using the table's primary
    keys as the index elements

    https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#insert-on-conflict-upsert
    """
    mapper = sqlalchemy.inspect(table)
    statement = sqlalchemy.dialects.postgresql.insert(table)

    set_ = {attr: statement.excluded[attr.key] for attr in mapper.column_attrs if attr not in mapper.primary_key}
    statement = statement.on_conflict_do_update(index_elements=mapper.primary_key, set_=set_)

    if instances:
        values: list[dict[typing.Any, typing.Any]] | dict[typing.Any, typing.Any]
        if isinstance(instances, typing.Sequence):
            values = [instance_to_dict(instance) for instance in instances]
        else:
            values = instance_to_dict(instances)
        statement = statement.values(values)

    return statement


class ISBN13(sqlalchemy.types.UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "ISBN13"

    def bind_expression(self, bindvalue: sqlalchemy.sql.elements.BindParameter):
        return sqlalchemy.func.isbn13(bindvalue, type_=self)

    @property
    def python_type(self):
        return str
