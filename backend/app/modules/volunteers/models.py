import uuid
from sqlalchemy import String, Enum as SAEnum, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Volunteer(Base):
    __tablename__ = "volunteers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum("active", "inactive", name="volunteer_status"), default="active"
    )
