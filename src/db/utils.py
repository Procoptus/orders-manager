from typing import Iterable

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from src.db.connection import get_engine
from src.db.models import BuyOrder, BuyOrderModel


def get_ids_from_db() -> set[str]:
    """Получить множество id из БД"""
    with Session(get_engine()) as session:
        stmt = select(BuyOrderModel.id)
        return set(session.scalars(stmt).all())


def delete_ids_from_db(ids: Iterable[str]):
    """Получить множество id из БД"""
    with Session(get_engine()) as session:
        stmt = delete(BuyOrderModel).where(BuyOrderModel.id.in_(ids))
        session.execute(stmt)
        session.commit()
