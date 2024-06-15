import datetime
import typing
import uuid

from flask import url_for
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .properties import StringProperty
from .base import Base

if typing.TYPE_CHECKING:
    from .work import Work


class Record(Base):
    __tablename__ = "record"

    work_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work.id", ondelete="CASCADE"))
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    time_created: Mapped[datetime.datetime] = mapped_column(default=func.now(), insert_default=func.now())
    time_updated: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None, onupdate=func.now())
    time_deleted: Mapped[typing.Optional[datetime.datetime]] = mapped_column(default=None)

    date_started: Mapped[typing.Optional[datetime.date]] = mapped_column(default=None)
    date_stopped: Mapped[typing.Optional[datetime.date]] = mapped_column(default=None)
    notes: Mapped[typing.Optional[str]] = mapped_column(default=None)

    work: Mapped["Work"] = relationship(back_populates="records", lazy="raise")

    @property
    def deleted(self) -> bool:
        return self.time_deleted is not None

    def url_for(self) -> str:
        return url_for("record.detail", work_id=self.work_id, record_id=self.id)

    def entry_properties(self):
        yield StringProperty("Started", self.date_started)
        yield StringProperty("Stopped", self.date_stopped)
