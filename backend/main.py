from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
import shutil
from datetime import datetime

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
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

# === API ===

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
        photo_path = f"uploads/{filename}"  # ← ВСЕГДА с "uploads/"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
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

@app.get("/api/catches")
async def get_catches():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM catches ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return JSONResponse([dict(row) for row in rows])

@app.delete("/api/catches/{catch_id}")
async def delete_catch(catch_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM catches WHERE id = ?", (catch_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Улов не найден")
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.patch("/api/catches/{catch_id}")
async def update_catch(
    catch_id: int,
    weight_kg: float = Form(...),
    length_cm: float = Form(...),
    photo: UploadFile = File(None)
):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT photo_path FROM catches WHERE id = ?", (catch_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Улов не найден")
    old_photo = row["photo_path"]
    photo_path = old_photo

    if photo and photo.filename:
        # Удаляем старое фото
        if old_photo and os.path.exists(old_photo):
            os.remove(old_photo)
        # Сохраняем новое
        ext = os.path.splitext(photo.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif"):
            raise HTTPException(status_code=400, detail="Неверный формат фото")
        filename = f"fish_{int(datetime.now().timestamp())}{ext}"
        photo_path = f"uploads/{filename}"  # ← ВСЕГДА с "uploads/"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

    cur.execute("""
        UPDATE catches
        SET weight_kg = ?, length_cm = ?, photo_path = ?
        WHERE id = ?
    """, (weight_kg, length_cm, photo_path, catch_id))
    conn.commit()
    conn.close()
    return {"status": "updated"}

# === Static files ===
# ВАЖНО: порядок имеет значение!
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")