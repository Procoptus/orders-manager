from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import registry, DeclarativeBase, mapped_column
from typing_extensions import Annotated

str32 = Annotated[str, 32]
str255 = Annotated[str, 255]
datetime_created = Annotated[datetime, mapped_column(nullable=False, default=datetime.now)]


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            datetime: TIMESTAMP(timezone=True),
            str32: String(32),
            str255: String(255),
        }
    )
