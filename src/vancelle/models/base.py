import typing

import sqlalchemy.orm
from werkzeug.exceptions import NotFound


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


class PolymorphicBase(Base):
    __abstract__ = True

    @classmethod
    def polymorphic_identity(cls) -> str:
        assert cls.__mapper__.polymorphic_identity is not None
        return cls.__mapper__.polymorphic_identity

    @classmethod
    def subclasses(cls) -> typing.Sequence[typing.Type[typing.Self]]:
        return list(
            sorted(
                (mapper.class_ for mapper in cls.__mapper__.polymorphic_map.values()),
                key=lambda c: c.info.priority,
                reverse=True,
            )
        )

    @classmethod
    def get_subclass(cls, name: str) -> typing.Type[typing.Self]:
        return cls.__mapper__.polymorphic_map[name].class_

    @classmethod
    def get_subclass_or_404(cls, name: str) -> typing.Type[typing.Self]:
        if name not in cls.__mapper__.polymorphic_map:
            raise NotFound(f"No {cls.__name__} type {name!r}")

        return cls.__mapper__.polymorphic_map[name].class_
