from pathlib import Path
from typing import Any
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..domain.file_item import FileItem
from ..domain.category import Category
from ..domain.tag import Tag

from ..domain.exceptions import DatabaseOperationError, ItemAlreadyExistsError
from .database.models import Base, FileItemModel, CategoryModel, TagModel


class LibraryRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        self.SessionLocal = sessionmaker(bind=self.engine)

        Base.metadata.create_all(self.engine)

    def _to_domain_file_item(self, db_file: FileItemModel) -> FileItem:
        return FileItem(
            name=db_file.name,
            absolute_path=db_file.absolute_path,
            extension=db_file.extension,
            id=db_file.id,
            category_id=db_file.category_id,
            tags=[Tag(name=tag.name, id=tag.id) for tag in db_file.tags],
            image_name=db_file.image_name,
            image_id=db_file.image_id,
        )

    def _to_domain_tag(self, db_tag: TagModel) -> Tag:
        return Tag(name=db_tag.name, id=db_tag.id)

    def _to_domain_category(self, db_category: CategoryModel) -> Category:
        return Category(name=db_category.name, id=db_category.id)

    def get_file_item(self, file_id: int) -> FileItem:
        with self.SessionLocal() as session:
            db_file = session.get(FileItemModel, file_id)
            if not db_file:
                raise DatabaseOperationError(f"FileItem with ID {file_id} not found.")

            return self._to_domain_file_item(db_file)

    def get_all_file_items(self) -> list[FileItem]:
        with self.SessionLocal() as session:
            db_files = session.query(FileItemModel).all()
            return [self._to_domain_file_item(db_file) for db_file in db_files]

    def get_tag(self, tag_id: int) -> Tag:
        with self.SessionLocal() as session:
            db_tag = session.get(TagModel, tag_id)
            if not db_tag:
                raise DatabaseOperationError(f"Tag with ID {tag_id} not found.")

            return self._to_domain_tag(db_tag)

    def get_all_tags(self) -> list[Tag]:
        with self.SessionLocal() as session:
            db_tags = session.query(TagModel).all()
            return [self._to_domain_tag(db_tag) for db_tag in db_tags]

    def get_category(self, category_id: int) -> Category:
        with self.SessionLocal() as session:
            db_category = session.get(CategoryModel, category_id)
            if not db_category:
                raise DatabaseOperationError(f"Category with ID {category_id} not found.")

            return self._to_domain_category(db_category)

    def get_all_categories(self) -> list[Category]:
        with self.SessionLocal() as session:
            db_categories = session.query(CategoryModel).all()
            return [self._to_domain_category(db_category) for db_category in db_categories]

    def save_file_item(self, item: FileItem) -> FileItem:
        with self.SessionLocal() as session:
            try:
                db_file = FileItemModel(
                    name=item.name,
                    absolute_path=item.absolute_path,
                    extension=item.extension,
                    image_name=item.image_name,
                    image_id=item.image_id,
                    category_id=item.category_id,
                )

                if item.tags:
                    for tag in item.tags:
                        db_tag = session.query(TagModel).filter_by(id=tag.id).first()
                        if db_tag:
                            db_file.tags.append(db_tag)

                session.add(db_file)
                session.commit()

                session.refresh(db_file)
                return self._to_domain_file_item(db_file)

            except IntegrityError as e:
                session.rollback()
                raise ItemAlreadyExistsError(f"Path or item already exists: {e}") from e
            except SQLAlchemyError as e:
                session.rollback()
                raise DatabaseOperationError(f"Failed to save to database: {e}") from e

    def update_file_image(self, file_id: int, image_name: str, image_id: int) -> FileItem:
        with self.SessionLocal() as session:
            db_file = session.get(FileItemModel, file_id)
            if not db_file:
                raise DatabaseOperationError(f"FileItem with ID {file_id} not found.")

            db_file.image_name = image_name
            db_file.image_id = image_id
            session.commit()
            session.refresh(db_file)

            return self._to_domain_file_item(db_file)

    def add_tag_to_file_item(self, file_id: int, tag_id: int) -> FileItem:
        with self.SessionLocal() as session:
            db_file = session.get(FileItemModel, file_id)
            if not db_file:
                raise DatabaseOperationError(f"FileItem with ID {file_id} not found.")

            db_tag = session.get(TagModel, tag_id)
            if not db_tag:
                raise DatabaseOperationError(f"Tag with ID {tag_id} not found.")

            if db_tag not in db_file.tags:
                db_file.tags.append(db_tag)

            session.commit()
            session.refresh(db_file)

            return self._to_domain_file_item(db_file)

    def remove_tag_from_file_item(self, file_id: int, tag_id: int) -> FileItem:
        with self.SessionLocal() as session:
            db_file = session.get(FileItemModel, file_id)
            if not db_file:
                raise DatabaseOperationError(f"FileItem with ID {file_id} not found.")

            db_tag = session.get(TagModel, tag_id)
            if not db_tag:
                raise DatabaseOperationError(f"Tag with ID {tag_id} not found.")

            if db_tag in db_file.tags:
                db_file.tags.remove(db_tag)

            session.commit()
            session.refresh(db_file)

            return self._to_domain_file_item(db_file)

    def set_file_category(self, file_id: int, category_id: int | None) -> FileItem:
        with self.SessionLocal() as session:
            db_file = session.get(FileItemModel, file_id)
            if not db_file:
                raise DatabaseOperationError(f"FileItem with ID {file_id} not found.")

            if category_id is not None:
                db_category = session.get(CategoryModel, category_id)
                if not db_category:
                    raise DatabaseOperationError(f"Category with ID {category_id} not found.")

            db_file.category_id = category_id
            session.commit()
            session.refresh(db_file)

            return self._to_domain_file_item(db_file)

    def remove_file_category(self, file_id: int) -> FileItem:
        return self.set_file_category(file_id=file_id, category_id=None)

    def delete_file_item(self, file_id: int) -> None:
        with self.SessionLocal() as session:
            db_file = session.query(FileItemModel).filter_by(id=file_id).first()
            if not db_file:
                raise DatabaseOperationError(f"FileItem with ID {file_id} not found.")

            session.delete(db_file)
            session.commit()

    def create_category(self, category: Category) -> Category:
        with self.SessionLocal() as session:
            try:
                db_category = CategoryModel(name=category.name)
                session.add(db_category)
                session.commit()
                session.refresh(db_category)

                category.id = db_category.id
                return category
            except IntegrityError as e:
                session.rollback()
                raise ItemAlreadyExistsError(f"Category '{category.name}' already exists.") from e

    def create_tag(self, tag: Tag) -> Tag:
        with self.SessionLocal() as session:
            try:
                db_tag = TagModel(name=tag.name)
                session.add(db_tag)
                session.commit()
                session.refresh(db_tag)

                tag.id = db_tag.id
                return tag
            except IntegrityError as e:
                session.rollback()
                raise ItemAlreadyExistsError(f"Tag '{tag.name}' already exists.") from e

    def delete_tag(self, tag_id: int) -> None:
        with self.SessionLocal() as session:
            db_tag = session.get(TagModel, tag_id)
            if not db_tag:
                raise DatabaseOperationError(f"Tag with ID {tag_id} not found.")

            session.delete(db_tag)
            session.commit()

    def delete_category(self, category_id: int) -> None:
        with self.SessionLocal() as session:
            db_category = session.get(CategoryModel, category_id)
            if not db_category:
                raise DatabaseOperationError(f"Category with ID {category_id} not found.")

            session.query(FileItemModel).filter_by(category_id=category_id).update(
                {FileItemModel.category_id: None},
                synchronize_session=False,
            )
            session.delete(db_category)
            session.commit()
