import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from jose import jwt, JWTError
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.responses import JSONResponse

from core.db import get_async_session
from core.models.models import User, Department
from core.schemas import UserLogin, UserCreateSchema, UserRead
from core.security import verify_password, create_access_token, SECRET_KEY, ALGORITHM, get_password_hash, \
    get_current_user

router = APIRouter(prefix='/api/auth', tags=['Login'])
error_logger = logging.getLogger("errors")
action_logger = logging.getLogger("actions")


###
# Взод пользователя.
# Создаем токен и отправляем его в виде cookie для сохранения в браузере
###
@router.post("/signin")
async def login(user: UserLogin, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        error_logger.error(f'Неудачная попытка входа: {user}')
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(data={
        "id": db_user.id,
        "username": db_user.username,
        "admin": db_user.admin
    })

    response = JSONResponse(content={
        "id": db_user.id,
        "username": db_user.username,
        "name": db_user.name,
        "admin": db_user.admin,
    },
    )
    # response.set_cookie(key="token", value=token, httponly=True, secure=True, samesite='none')
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,  # разрешаем HTTP
        samesite="lax"  # или 'strict' — в зависимости от логики
    )

    action_logger.info(f'Пользователь {db_user.username} вошел в систему')
    return response


@router.get("/user_info", response_model=UserRead)
async def get_user_info(user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(User).where(User.id == user.id).options(joinedload(User.department))
    )
    user = result.scalar_one_or_none()
    if not user:
        error_logger.error('Пользователь не найдень')
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


###
# Выход из учетной записи.
# Удаляем token
###
@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("token")
    action_logger.info(f'Пользователь {user.id} вышел из системы')
    return response


###
# Проверяем существует ли пользователь и его авторизация актуальна, для действий с обязательной авторизацией
###
@router.get("/check_auth")
async def get_me(request: Request, db: AsyncSession = Depends(get_async_session)):
    token = request.cookies.get("token")
    if not token:
        error_logger.error(f'Ошибка проверки аутентификации, нет токена')
        raise HTTPException(status_code=401, detail="Not authenticated, token is missing")

    payload = decode_access_token(token)
    user_id = payload.get("id")

    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        error_logger.error(f'Ошибка проверки аутентификации, пользователь не найден')
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": db_user.id,
        "username": db_user.username,
        "name": db_user.name,
        "admin": db_user.admin
    }


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        error_logger.error(f'Ошибка проверки токена')
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


###
# Регистрация пользователя
###
@router.post("/signup")
async def register_user(
        user_data: UserCreateSchema,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)):
    # Проверка уникальности логина
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        error_logger.error(f'Ошибка регистрации пользователя, такой пользователь уже существует')
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    # Проверка существования департамента
    department_result = await db.execute(select(Department).where(Department.id == user_data.department_id))
    department = department_result.scalar_one_or_none()
    if not department:
        error_logger.error(f'Ошибка регистрации пользователя, не найден указанная служба')
        raise HTTPException(status_code=400, detail="Указанная служба не существует")

    # Получаем максимальный id
    max_id_result = await db.execute(select(func.max(User.id)))
    max_id = max_id_result.scalar() or 0
    next_id = max_id + 1

    new_user = User(
        id=next_id,  # Указываем ID вручную
        username=user_data.username,
        password=get_password_hash(user_data.password),
        name=user_data.name,
        department_id=user_data.department_id,
        admin=getattr(user_data, 'admin', False)  # Поддержка admin поля
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    action_logger.info(f'{user} содал учетную запись: {new_user}')
    return {"message": "Пользователь создан", "user_id": new_user.id}
