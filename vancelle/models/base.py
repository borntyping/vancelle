import typing

import sqlalchemy.orm


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


class PolymorphicBase(Base):
    __abstract__ = True

    @classmethod
    def polymorphic_identity(cls) -> str:
        assert cls.__mapper__.polymorphic_identity is not None
        return cls.__mapper__.polymorphic_identity

    @classmethod
    def iter_subclasses(cls) -> typing.Sequence[typing.Type[typing.Self]]:
        return list(
            sorted(
                (mapper.class_ for mapper in cls.__mapper__.polymorphic_map.values()),
                key=lambda c: c.info.priority,
                reverse=True,
            )
        )

    @classmethod
    def get_subclass(cls, name: str) -> typing.Type[typing.Self]:
        return cls.__mapper__.polymorphic_map[name]
