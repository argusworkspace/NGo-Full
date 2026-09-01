import uuid
from sqlalchemy import String, Numeric, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import datetime


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "completed", "draft", name="program_status"), default="draft"
    )
    start_date: Mapped[datetime.date] = mapped_column(Date)
    end_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    budget: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
