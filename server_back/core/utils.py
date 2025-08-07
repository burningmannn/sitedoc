import os
import uuid
from datetime import datetime

from fastapi import UploadFile

UPLOAD_DIR = "uploads"


async def save_file_with_uuid(file: UploadFile) -> tuple[str, str]:
    # Расширение файла
    ext = os.path.splitext(file.filename)[-1]

    # Уникальное имя
    unique_filename = f"{uuid.uuid4()}{ext}"

    # Папка по дате (напр. uploads/2025/04/17/)
    date_path = datetime.now().strftime("%Y/%m/%d")
    save_dir = os.path.join(UPLOAD_DIR, date_path)
    os.makedirs(save_dir, exist_ok=True)

    # Полный путь к файлу
    full_path = os.path.join(save_dir, unique_filename)

    # Сохранение файла
    with open(full_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return full_path, file.filename  # путь к файлу и оригинальное имя
