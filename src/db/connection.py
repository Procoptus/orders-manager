from sqlalchemy import create_engine

from src.config import config
from src.db.base import Base


engine = None


def get_engine():
    global engine
    if not engine:
        engine = create_engine(config['DB_URL'], echo=False)
        Base.metadata.create_all(engine)
    return engine
