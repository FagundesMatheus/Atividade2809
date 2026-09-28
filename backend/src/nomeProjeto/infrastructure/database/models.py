from typing import List, Optional
from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


file_item_tags = Table(
    "file_item_tags",
    Base.metadata,
    Column(
        "file_item_id",
        ForeignKey("file_items.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class TagModel(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class FileItemModel(Base):
    __tablename__ = "file_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    absolute_path: Mapped[str] = mapped_column(String, unique=True)
    extension: Mapped[str] = mapped_column(String)

    image_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    image_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    category: Mapped[Optional["CategoryModel"]] = relationship()

    tags: Mapped[List["TagModel"]] = relationship(secondary=file_item_tags, backref="file_items")
