from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import shutil
from datetime import datetime

app = FastAPI()

# Папка для загруженных фото
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Раздача статики: фронтенд и загруженные файлы
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Путь к базе данных
DB_PATH = "catches.db"

def init_db():
    """Создаёт таблицу, если её нет"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE catches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight_kg REAL NOT NULL,
                length_cm REAL NOT NULL,
                photo_path TEXT
            )
        """)
        conn.commit()
        conn.close()

# Инициализация БД при старте
init_db()

@app.get("/", response_class=HTMLResponse)
async def index():
    """Отдаёт главную HTML-страницу"""
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/api/catches")
async def create_catch(
    weight_kg: float = Form(...),
    length_cm: float = Form(...),
    photo: UploadFile = File(None)
):
    """Сохраняет новый улов с фото (опционально)"""
    photo_path = None
    if photo and photo.filename:
        # Проверка расширения
        ext = os.path.splitext(photo.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif"):
            return JSONResponse({"error": "Разрешены только JPG, PNG, GIF"}, status_code=400)
        # Уникальное имя файла
        filename = f"fish_{int(datetime.now().timestamp())}{ext}"
        photo_path = os.path.join(UPLOAD_DIR, filename)
        # Сохранение файла
        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

    # Сохранение в БД
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO catches (weight_kg, length_cm, photo_path) VALUES (?, ?, ?)",
        (weight_kg, length_cm, photo_path)
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/catches")
async def get_catches():
    """Возвращает список всех уловов"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Позволяет обращаться по имени колонки
    cur = conn.cursor()
    cur.execute("SELECT * FROM catches ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    # Преобразуем в список словарей
    return JSONResponse([dict(row) for row in rows])