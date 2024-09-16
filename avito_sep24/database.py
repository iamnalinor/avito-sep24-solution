import datetime
import uuid
from collections.abc import Iterator
from typing import Any

from sqlalchemy import DateTime, Uuid, create_engine, func
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    sessionmaker,
)

from avito_sep24.env import POSTGRES_CONN

engine = create_engine(POSTGRES_CONN)
make_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
RawBase: type[Any] = declarative_base()


class Base(RawBase):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        nullable=False,
    )


def get_session() -> Iterator[Session]:
    db = make_session()
    try:
        yield db
    finally:
        db.close()
