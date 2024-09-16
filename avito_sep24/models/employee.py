from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from avito_sep24.database import Base


class Employee(Base):
    __tablename__ = "employee"

    username: Mapped[str] = mapped_column(String(length=50), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(length=50))
    last_name: Mapped[str | None] = mapped_column(String(length=50))
