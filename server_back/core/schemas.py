from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel
from pydantic.utils import GetterDict


class DepTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    name: str
    department: Optional[DepTypeOut] = None  # ✅ имя совпадает с моделью
    create_at: datetime
    admin: bool

    class Config:
        from_attributes = True
        populate_by_name = True


class DocTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
        orm_mode = True


class DocumentGetter(GetterDict):
    def get(self, key, default=None):
        if key == "doc_type":
            return self._obj.doc_type.name if self._obj.doc_type else None
        return super().get(key, default)


class DocTypeUpdate(BaseModel):
    name: str


class DocumentOut(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    permanent: Optional[bool] = None
    file_number: Optional[str] = None
    doc_type: DocTypeOut
    responsible: Optional[DepTypeOut]
    valid_until: Optional[date] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True  # ✅ для Pydantic 2


class NotificationCreate(BaseModel):
    file_id: int
    message: str


class RouteStepOut(BaseModel):
    id: int
    responsible: str

    class Config:
        orm_mode = True


class RouteOut(BaseModel):
    id: int
    name: str
    steps: List[RouteStepOut]

    class Config:
        orm_mode = True


class UserCreateSchema(BaseModel):
    username: str
    password: str
    name: str
    department_id: int
    admin: Optional[bool] = False

    class Config:
        orm_mode = True


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    department_id: Optional[int] = None
    admin: Optional[bool] = None

    create_at: Optional[str] = None
    id: Optional[int] = None
