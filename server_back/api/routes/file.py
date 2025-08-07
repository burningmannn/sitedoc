import logging
import os
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import FileResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.db import get_async_session
from core.models.models import Document, User, DocType, Notification, Responsible, Department
from core.schemas import DocumentOut
from core.security import get_current_user, get_optional_user
from core.utils import save_file_with_uuid

router = APIRouter(prefix='/api/file', tags=['File'])
error_logger = logging.getLogger("errors")
action_logger = logging.getLogger("actions")


@router.post("/upload")
async def upload_with_route(
        file: UploadFile = File(...),
        responsible: str = Form(...),
        doc_type: str = Form(...),
        doc_number: Optional[str] = Form(None),
        is_permanent: Optional[bool] = Form(False),
        valid_until: Optional[date] = Form(None),
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user),
):
    doc_type_obj = await db.get(DocType, int(doc_type))
    if not doc_type_obj:
        raise HTTPException(status_code=404, detail="Тип документа не найден")

    path, original_name = await save_file_with_uuid(file)

    new_doc = Document(
        filename=os.path.basename(path),
        original_filename=original_name,
        file_path=path,
        doc_type_id=doc_type_obj.id,
        responsible_id=int(responsible),
        valid_until=valid_until,
        uploaded_by=user.id,
        uploaded_at=datetime.utcnow(),
        permanent=is_permanent,
        file_number=doc_number,
    )

    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    responsible_users = await db.execute(
        select(Responsible).where(Responsible.department_id == int(responsible))
    )

    for resp in responsible_users.scalars():
        db.add(Notification(
            file_id=new_doc.id,
            user_id=resp.user_id,
            message=f'Вам назначен новый файл: {original_name}'
        ))

    action_logger.info(f"Пользователь {user.id} загрузил файл: {original_name}")
    await db.commit()

    return {"message": "Документ загружен и маршрут применён", "id": new_doc.id}


@router.get("/all", response_model=List[DocumentOut])
async def get_files(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(Document).options(
            joinedload(Document.doc_type),
            joinedload(Document.responsible)
        ).order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


@router.get("/download/{file_id}")
async def get_file(file_id: int, db: AsyncSession = Depends(get_async_session),
                   user: Optional[User] = Depends(get_optional_user)):
    doc = await db.get(Document, file_id)
    if not doc or not os.path.exists(doc.file_path):
        error_logger.error(f'Ошибка скачивания файла: {file_id}')
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(doc.file_path, media_type="application/octet-stream",
                        filename=doc.original_filename + Path(doc.file_path).suffix)


@router.get("/info/{file_id}")
async def get_file_info(file_id: int, db: AsyncSession = Depends(get_async_session),
                        user: User = Depends(get_optional_user)):
    doc = await db.get(Document, file_id)
    if not doc:
        error_logger.error(f'Ошибка получения файла: {file_id}')
        raise HTTPException(status_code=404, detail="Файл не найден")
    return {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "doc_number": doc.file_number,
        "doc_type": doc.doc_type,
        "responsible": doc.responsible,
        "valid_until": doc.valid_until.isoformat() if doc.valid_until else None,
        "permanent": doc.permanent,
    }


@router.get("/my")
async def get_my_files(db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    # Получаем документы, загруженные пользователем
    result = await db.execute(
        select(Document)
        .where(Document.uploaded_by == user.id)
        .order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()
    document_ids = [doc.id for doc in documents]

    if not document_ids:
        return []

    # Загружаем уведомления + ответственные + пользователи + отделы
    result = await db.execute(
        select(Notification, Responsible, User, Department)
        .join(Responsible, Responsible.user_id == Notification.user_id)
        .join(User, User.id == Responsible.user_id)
        .join(Department, Department.id == Responsible.department_id)
        .where(Notification.file_id.in_(document_ids))
    )
    rows = result.all()

    # Словарь: doc_id -> {"read_by": {user_id: {...}}, "unread_by": {user_id: {...}}}
    notifications_by_doc = defaultdict(lambda: {"read_by": {}, "unread_by": {}})

    for note, responsible, user_obj, department in rows:
        user_key = user_obj.id
        responsible_info = {
            "department_id": department.name,
            "user_id": user_obj.name
        }
        group = "read_by" if note.is_read else "unread_by"
        # Добавляем только если такого пользователя ещё нет
        if user_key not in notifications_by_doc[note.file_id][group]:
            notifications_by_doc[note.file_id][group][user_key] = responsible_info

    # Формируем ответ
    response = []
    for doc in documents:
        notif = notifications_by_doc.get(doc.id, {"read_by": {}, "unread_by": {}})
        read_by = list(notif["read_by"].values())
        unread_by = list(notif["unread_by"].values())

        response.append({
            "id": doc.id,
            "original_filename": doc.original_filename,
            "doc_type": doc.doc_type,
            "valid_until": doc.valid_until,
            "uploaded_at": doc.uploaded_at,
            "total_responsibles": len(read_by) + len(unread_by),
            "read_count": len(read_by),
            "unread_count": len(unread_by),
            "read_by": read_by,
            "unread_by": unread_by,
        })

    return response


@router.get("/inwork")
async def get_files_in_work(db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    notifications = await db.execute(select(Notification).where(Notification.user_id == user.id))
    docs = []
    for notif in notifications.scalars():
        doc = await db.get(Document, notif.file_id)
        if doc:
            docs.append(doc)
    return [{
        "id": doc.id,
        "original_filename": doc.original_filename,
        "doc_type": doc.doc_type,
        "responsible": doc.responsible,
        "valid_until": doc.valid_until
    } for doc in docs]


@router.put("/update/{file_id}")
async def update_file(file_id: int, data: dict = Body(...), db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(get_current_user)):
    doc = await db.get(Document, file_id)
    if not doc or doc.uploaded_by != user.id:
        error_logger.error(f'Ошибка обновления файла: {file_id}')
        raise HTTPException(status_code=404, detail="Файл не найден или доступ запрещён")

    if "doc_type" in data:
        doc_type = await db.get(DocType, data["doc_type"]["id"])
        if not doc_type:
            raise HTTPException(status_code=404, detail="Тип документа не найден")
        doc.doc_type = doc_type

    if "responsible" in data:
        responsible = await db.get(Department, data["responsible"].get("id"))
        if responsible:
            doc.responsible = responsible
        else:
            raise HTTPException(status_code=404, detail="Ответственный не найден")

    doc.permanent = data.get("permanent", doc.permanent)
    doc.file_number = data.get("doc_number", doc.file_number)
    doc.original_filename = data.get("original_filename", doc.original_filename)

    valid_until_raw = data.get("valid_until")
    if valid_until_raw:
        try:
            doc.valid_until = datetime.fromisoformat(valid_until_raw.split("T")[0]).date() + timedelta(
                days=1)  # Костыль, из-за временных зон. Если убрать, то при редактировании дата окончания документа
            #  будет на один день меньше
            print(doc.valid_until)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты")

    await db.commit()
    action_logger.info(f"Пользователь {user.id} обновил файл: {doc.original_filename}")
    return {"status": "ok"}


@router.post("/replace/{file_id}")
async def replace_file(
        file_id: int,
        file: UploadFile = File(...),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    doc = await db.get(Document, file_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Файл не найден")
    if doc.uploaded_by != user.id and user.admin is not True:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    # Удаление старого файла, если он существует
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка удаления файла: {e}")

    # Сохранение нового файла
    new_path, new_name = await save_file_with_uuid(file)

    # Обновляем документ
    doc.filename = os.path.basename(new_path)
    doc.original_filename = new_name
    doc.file_path = new_path
    doc.uploaded_at = datetime.utcnow()  # если нужно обновить дату замены

    await db.commit()
    await db.refresh(doc)

    return {
        "status": "file replaced",
        "id": doc.id,
        "original_filename": doc.original_filename,
        "filename": doc.filename,
        "uploaded_at": doc.uploaded_at,
    }


@router.delete("/delete/{file_id}")
async def delete_file(file_id: int, db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(get_current_user)):
    doc = await db.get(Document, file_id)
    if not doc or (doc.uploaded_by != user.id and not user.admin):
        error_logger.error(f'Ошибка удаления файла {file_id}')
        raise HTTPException(status_code=403, detail="Файл не найден или недостаточно прав")

    await db.execute(delete(Notification).where(Notification.file_id == file_id))  # Удаление уведомлений на этот файл
    await db.delete(doc)
    await db.commit()

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    action_logger.info(f'Пользователь {user.id} удалил файл {file_id}')
    return {"status": "deleted"}


@router.get("/doc-type")
async def get_all_doc_types_and_departments(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(DocType))
    doc_types = result.scalars().all()
    if not doc_types:
        raise HTTPException(status_code=404, detail="Типы документов не найдены")
    return doc_types
