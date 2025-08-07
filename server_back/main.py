import logging
import os

import uvicorn
from asyncpg import InvalidCatalogNameError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from api.routes.admin import router as admin_routes
from api.routes.file import router as router_file
from api.routes.login import router as router_auth
from api.routes.notification import router as router_notification
from core.apsched import backup_postgres
from core.config import settings, init_logging
from core.db import engine, Base
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

errors_logger = logging.getLogger("errors")
actions_logger = logging.getLogger("actions")


async def init_db():
    try:
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        actions_logger.info("База данных инициализирована.")
    except InvalidCatalogNameError as e:
        errors_logger.error(f"База данных не найдена: {e}")
        raise
    except SQLAlchemyError as e:
        errors_logger.exception("Ошибка SQLAlchemy при инициализации базы данных.")
        raise
    except Exception as e:
        errors_logger.exception("Непредвиденная ошибка при инициализации базы данных.")
        raise


def create_app() -> FastAPI:
    app = FastAPI()
    origins = [
        "http://localhost:3000",  # адрес Nuxt фронтенда
        "http://192.168.1.76:3000",  # локальный IP, если с другого устройства
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # или ["*"] во время разработки
        allow_credentials=True, #
        allow_methods=["*"],
        allow_headers=["*"],
    )
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    app.include_router(router_auth)
    app.include_router(router_file)
    app.include_router(router_notification)
    app.include_router(admin_routes)

    return app


app = create_app()


@app.on_event("startup")
async def startup_event():
    await init_db()

    # 🕒 Бэкап в 03:00 каждый день
    scheduler.add_job(backup_postgres, trigger='cron', hour=14, minute=34, id='backup_postgres')

    scheduler.start()

    init_logging()
    action_logger = logging.getLogger("actions")
    action_logger.info("Приложение запущено.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

