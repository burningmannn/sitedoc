import datetime
from typing import List

from sqlalchemy import ForeignKey, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False
    )
    create_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    admin: Mapped[bool] = mapped_column(default=False)

    department: Mapped["Department"] = relationship(
        back_populates="users",
        passive_deletes=True
    )
    responsibilities: Mapped[List["Responsible"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __str__(self):
        return f'{self.__class__} {self.id=} {self.name=!r} {self.department_id=} {self.create_at=} {self.admin=}'

    def __repr__(self):
        return str(self)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    filename: Mapped[str] = mapped_column(nullable=False)
    original_filename: Mapped[str] = mapped_column(nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    file_number: Mapped[str] = mapped_column(nullable=True)

    doc_type_id: Mapped[int] = mapped_column(
        ForeignKey("doc_types.id", ondelete="SET NULL"),
        nullable=False
    )
    responsible_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True
    )
    permanent: Mapped[bool] = mapped_column(nullable=True)

    valid_until: Mapped[datetime.date] = mapped_column(nullable=True)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    doc_type = relationship(
        "DocType",
        back_populates="documents",
        lazy="joined",
        passive_deletes=True
    )
    notifications = relationship(
        "Notification",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    responsible = relationship(
        "Department",
        back_populates="documents",
        lazy="joined",
        passive_deletes=True
    )

    def __str__(self):
        return (f"Document(id={self.id}, original_filename='{self.original_filename}', "
                f"responsible='{self.responsible}', doc_type='{self.doc_type.name if self.doc_type else None}')")

    def __repr__(self):
        return str(self)


class DocType(Base):
    __tablename__ = "doc_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    documents = relationship(
        "Document",
        back_populates="doc_type",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __str__(self):
        return f"DocType(id={self.id}, name='{self.name}'"

    def __repr__(self):
        return str(self)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    is_read: Mapped[bool] = mapped_column(default=False)

    document = relationship("Document", back_populates="notifications")

    def __str__(self):
        return (f"Notification(id={self.id}, original_filename='{self.file_id}', original_filename='{self.user_id}'"
                f", original_filename='{self.created_at}', original_filename='{self.message}',"
                f" original_filename='{self.is_read}'")

    def __repr__(self):
        return str(self)


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="department")
    responsibles: Mapped[List["Responsible"]] = relationship(
        back_populates="department", cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        back_populates="responsible",
        passive_deletes=True
    )

    def __str__(self):
        return (f"Department(id={self.id}, original_filename='{self.name}', original_filename='{self.users},"
                f" original_filename='{self.responsibles}, original_filename='{self.documents} ")

    def __repr__(self):
        return str(self)


class Responsible(Base):
    __tablename__ = "responsibles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    user = relationship("User", back_populates="responsibilities", lazy="joined")
    department = relationship("Department", back_populates="responsibles", lazy="joined")

    def __repr__(self):
        return f"<Responsible user_id={self.user_id} department_id={self.department_id}>"
