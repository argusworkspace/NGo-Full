import uuid
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Donor(Base):
    __tablename__ = "donors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_donated: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
