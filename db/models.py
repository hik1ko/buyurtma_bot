from db.config import engine

from sqlalchemy import Column, DateTime, BigInteger, VARCHAR, Boolean, FLOAT, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from datetime import datetime, timezone, timedelta
from typing import Optional

TASHKENT_TZ = timezone(timedelta(hours=5))


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'


class CreatedModel(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(TASHKENT_TZ))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(TASHKENT_TZ),
                        onupdate=lambda: datetime.now(TASHKENT_TZ))


class User(CreatedModel):
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]] = mapped_column(VARCHAR(255), nullable=True)
    full_name: Mapped[str] = mapped_column(VARCHAR(1000))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return self.full_name

class Order(CreatedModel):
    client_name: Mapped[str] = mapped_column(VARCHAR(255))
    phone_number: Mapped[str] = mapped_column(VARCHAR(15))
    address: Mapped[str] = mapped_column(VARCHAR(255))
    longitude: Mapped[float] = mapped_column(FLOAT)
    latitude: Mapped[float] = mapped_column(FLOAT)
    product: Mapped[str] = mapped_column(VARCHAR(255))
    price: Mapped[int] = mapped_column(BigInteger)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    delivery_status: Mapped[str] = mapped_column(VARCHAR(255), default="Yetkazib berilmoqda")
    payment_method: Mapped[str] = mapped_column(VARCHAR(255))
    is_payment_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    comment: Mapped[str] = mapped_column(VARCHAR(1000), nullable=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)


Base.metadata.create_all(engine)
