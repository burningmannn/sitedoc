import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from starlette.responses import PlainTextResponse

from core.db import get_async_session
from core.models.models import DocType, Department, User, Responsible
from core.schemas import UserRead, UserUpdateSchema, DocTypeUpdate
from core.security import get_password_hash, get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])

action_logger = logging.getLogger("actions")
errors_logger = logging.getLogger("errors")


def read_last_lines(path: Path, num_lines: int = 200) -> str:
    """Чтение последних строк из лог-файла."""
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8") as file:
        return ''.join(file.readlines()[-num_lines:])


@router.post("/doc-type")
async def add_doc_type(
    name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Создание нового типа документа."""
    new_type = DocType(name=name)
    db.add(new_type)
    await db.commit()
    await db.refresh(new_type)
    action_logger.info(f"Пользователь {user.id} создал тип документа: {new_type.name}")
    return new_type


@router.get("/users", response_model=List[UserRead])
async def get_users(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получение списка всех пользователей."""
    result = await db.execute(
        select(User).options(joinedload(User.department))
    )
    users = result.scalars().all()
    if not users:
        errors_logger.error('Пользователи не найдены')
        raise HTTPException(status_code=404, detail="Пользователи не найдены")
    return users


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Обновление информации о пользователе."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        errors_logger.error('Пользователь не найден')
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_data.username is not None:
        user.username = user_data.username
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.department_id is not None:
        user.department_id = user_data.department_id
    if user_data.password:
        user.password = get_password_hash(user_data.password)

    await db.commit()
    await db.refresh(user)

    action_logger.info(f"Пользователь {current_user.id} обновил информацию о пользователе {user.id}")
    return {"message": "Пользователь обновлён", "user_id": user.id}


@router.post("/assign/{department_id}/")
async def assign_user_to_department(
    department_id: int,
    data: dict = Body(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Назначение пользователя ответственным за службу."""
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    responsible = Responsible(user_id=user_id, department_id=department_id)
    db.add(responsible)
    await db.commit()
    action_logger.info(f"Пользователь {user.id} назначил ответственным {responsible.user_id} за службу {department_id}")
    return {"status": "ok"}


@router.delete("/assign/{responsible_id}/")
async def remove_responsible(
    responsible_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаление ответственного за службу."""
    result = await db.execute(select(Responsible).where(Responsible.id == responsible_id))
    responsible = result.scalar_one_or_none()
    if not responsible:
        raise HTTPException(status_code=404, detail="Ответственный не найден")

    await db.delete(responsible)
    await db.commit()
    action_logger.info(f"Пользователь {user.id} удалил ответственного {responsible.user_id} из службы {responsible.department_id}")
    return {"message": "Ответственный удалён"}


@router.get("/assign/")
async def list_responsibles(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Список всех ответственных по службам."""
    result = await db.execute(
        select(Responsible).options(joinedload(Responsible.user), joinedload(Responsible.department))
    )
    responsibles = result.scalars().all()

    return [
        {
            "id": r.id,
            "user_name": r.user.name,
            "user_id": r.user_id,
            "department_id": r.department_id,
            "department_name": r.department
        }
        for r in responsibles
    ]


@router.put("/doc-type/{id}")
async def update_doc_type(
    id: int,
    data: DocTypeUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Обновление типа документа."""
    result = await db.execute(select(DocType).where(DocType.id == id))
    doc_type = result.scalar_one_or_none()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Тип документа не найден")

    doc_type.name = data.name
    await db.commit()
    action_logger.info(f"Пользователь {user.id} обновил тип документа: {data.name}")
    return doc_type


@router.delete("/doc-type/{id}")
async def delete_doc_type(
    id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаление типа документа."""
    result = await db.execute(select(DocType).where(DocType.id == id))
    doc_type = result.scalar_one_or_none()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Тип документа не найден")

    await db.delete(doc_type)
    await db.commit()
    action_logger.info(f"Пользователь {user.id} удалил тип документа {id}")
    return {"status": "deleted"}


@router.delete("/users/{id}")
async def delete_user(
    id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаление пользователя."""
    result = await db.execute(select(User).where(User.id == id))
    user_result = result.scalar_one_or_none()
    if not user_result:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await db.delete(user_result)
    await db.commit()
    action_logger.info(f"Пользователь {user.id} удалил пользователя {user_result.id}")
    return {"status": "deleted"}


@router.get("/department")
async def get_departments(db: AsyncSession = Depends(get_async_session)):
    """Получение всех служб (департаментов)."""
    result = await db.execute(select(Department).order_by(Department.name.asc()))
    departments = result.scalars().all()
    if departments is None:
        raise HTTPException(status_code=404, detail="Службы не найдены")
    return departments


@router.post("/department")
async def add_department(
    name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Создание новой службы."""
    department = Department(name=name)
    db.add(department)
    await db.commit()
    await db.refresh(department)
    action_logger.info(f"Пользователь {user.id} создал службу {name}")
    return department


@router.put("/department/{id}")
async def update_department(
    id: int,
    name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Изменение службы."""
    result = await db.execute(select(Department).where(Department.id == id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(status_code=404, detail="Служба не найдена")

    department.name = name
    await db.commit()
    action_logger.info(f"Пользователь {user.id} изменил службу {name}")
    return department


@router.delete("/department/{id}")
async def delete_department(
    id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаление службы, если к ней не привязаны пользователи."""
    result = await db.execute(select(Department).where(Department.id == id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(status_code=404, detail="Служба не найдена")

    user_check = await db.execute(select(User).where(User.department_id == id))
    if user_check.scalars().all():
        raise HTTPException(status_code=400, detail="Нельзя удалить службу — к ней привязаны пользователи")

    await db.delete(department)
    await db.commit()
    action_logger.info(f"Пользователь {user.id} удалил службу {id}")
    return {"status": "deleted"}


@router.patch("/department/assign-responsible/{department_id}")
async def assign_responsible_user(
    department_id: int,
    user_id: int = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Назначение ответственного пользователя для службы."""
    result = await db.execute(select(Department).where(Department.id == department_id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(status_code=404, detail="Служба не найдена")

    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    department.responsible_user_id = user_id
    await db.commit()
    action_logger.info(f"Пользователь {user.id} назначил {target_user.id} ответственным за службу {department.name}")
    return {"message": "Ответственный назначен", "department_id": department_id, "user_id": user_id}


@router.get("/actions", response_class=PlainTextResponse)
async def get_action_log(user: User = Depends(get_current_user)):
    """Получение лога действий (только для админов)."""
    if not user.admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return read_last_lines(Path("logs/actions.log"), num_lines=300)


@router.get("/errors", response_class=PlainTextResponse)
async def get_error_log(user: User = Depends(get_current_user)):
    """Получение лога ошибок (только для админов)."""
    if not user.admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return read_last_lines(Path("logs/errors.log"), num_lines=300)
