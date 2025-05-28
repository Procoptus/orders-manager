from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.orm import Mapped, mapped_column, Session

from src.db.base import str32, datetime_created, Base, str255
from src.db.connection import get_engine


class BuyOrderModel(Base):
    __tablename__ = 'buy_orders'

    id: Mapped[str255] = mapped_column(primary_key=True)
    steam_id: Mapped[str32]
    quantity: Mapped[int]
    price: Mapped[float]
    item_name: Mapped[str255]
    game_name: Mapped[str255]
    created_at: Mapped[datetime_created]

    def save_to_db(self):
        with Session(get_engine()) as session:
            session.add(self)
            session.commit()

    def delete_from_db(self):
        with Session(get_engine()) as session:
            stmt = delete(self.__class__).where(self.__class__.id == self.id)
            session.execute(stmt)
            session.commit()

    def to_dataclass(self) -> "BuyOrder":
        return BuyOrder(**{c.name: getattr(self, c.name) for c in self.__table__.columns})


# Отзеркалил в dataclass, т.к. сессия с БД может быть уже закрыта, когда мы захотим получить инфу по атрибутам и в таком
# случае будет вызываться DetachedInstanceError
@dataclass
class BuyOrder:
    id: str
    steam_id: str
    quantity: int
    price: float
    item_name: str
    game_name: str
    created_at: datetime = field(default_factory=datetime.now)

    def save_to_db(self):
        BuyOrderModel(**self.__dict__).save_to_db()

    def delete_from_db(self):
        BuyOrderModel(**self.__dict__).delete_from_db()
