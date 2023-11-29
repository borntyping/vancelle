import typing
import uuid

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base, UserMixin):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

    works: Mapped[typing.List["Work"]] = relationship(back_populates="user", viewonly=True, lazy="dynamic")

    def get_id(self) -> str:
        return str(self.id)
