import datetime
import enum
import typing
import uuid

from flask import url_for
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .properties import StringProperty
from .base import Base

if typing.TYPE_CHECKING:
    from .work import Work


class RelativeDate(enum.Enum):
    today = enum.auto()
    yesterday = enum.auto()


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
        return url_for("record.detail", record_id=self.id)

    def url_for_update(self) -> str:
        return url_for("record.update", record_id=self.id)

    def url_for_delete(self) -> str:
        return url_for("record.delete", record_id=self.id)

    def url_for_restore(self) -> str:
        return url_for("record.restore", record_id=self.id)

    def url_for_permanently_delete(self) -> str:
        return url_for("record.permanently_delete", record_id=self.id)

    def entry_properties(self):
        yield StringProperty("Started", self.date_started)
        yield StringProperty("Stopped", self.date_stopped)

    def set_date_started(self, relative: RelativeDate | None, /):
        if relative is None:
            return
        elif self.date_started:
            raise ValueError("Record already has a started date")
        elif relative is RelativeDate.today:
            self.date_started = datetime.date.today()
        elif relative is RelativeDate.yesterday:
            self.date_started = datetime.date.today() - datetime.timedelta(days=1)
        else:
            raise ValueError(f"Unexpected value {relative=}")

    def set_date_stopped(self, relative: RelativeDate | None, /):
        if relative is None:
            return
        elif self.date_stopped:
            raise ValueError("Record already has a stopped date")
        elif relative is RelativeDate.today:
            self.date_stopped = datetime.date.today()
        elif relative is RelativeDate.yesterday:
            self.date_stopped = datetime.date.today() - datetime.timedelta(days=1)
        else:
            raise ValueError(f"Unexpected value {relative=}")
