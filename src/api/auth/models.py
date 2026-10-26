from typing import List, TYPE_CHECKING
from src.core.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.api.media.models import VideoItem, AudioItem

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)

    # Две отдельные связи вместо одной
    video_items: Mapped[List["VideoItem"]] = relationship(back_populates="owner")
    audio_items: Mapped[List["AudioItem"]] = relationship(back_populates="owner")