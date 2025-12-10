from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import shutil
from datetime import datetime

app = FastAPI()

# Папка для загрузок
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Раздаём фронтенд и загруженные файлы
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

DB_PATH = "catches.db"

def init_db():
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

init_db()

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/api/catches")
async def create_catch(
    weight_kg: float = Form(...),
    length_cm: float = Form(...),
    photo: UploadFile = File(None)
):
    photo_path = None
    if photo and photo.filename:
        # Генерируем уникальное имя: timestamp + оригинальное расширение
        ext = os.path.splitext(photo.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif"):
            return JSONResponse({"error": "Только JPG, PNG, GIF"}, status_code=400)
        filename = f"fish_{int(datetime.now().timestamp())}{ext}"
        photo_path = os.path.join(UPLOAD_DIR, filename)
        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO catches (weight_kg, length_cm, photo_path) VALUES (?, ?, ?)",
        (weight_kg, length_cm, photo_path)
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.post("/api/catches")
async def create_catch(
    weight_kg: float = Form(...),
    length_cm: float = Form(...),
    photo: UploadFile = File(None)
):
    photo_path = None
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif"):
            return JSONResponse({"error": "Только JPG, PNG, GIF"}, status_code=400)
        filename = f"fish_{int(datetime.now().timestamp())}{ext}"
        photo_path = os.path.join(UPLOAD_DIR, filename)
        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO catches (weight_kg, length_cm, photo_path) VALUES (?, ?, ?)",
        (weight_kg, length_cm, photo_path)  # ← здесь должно быть photo_path, НЕ строка с комментарием!
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}