# FishBook — Итерация 1

## Описание
Минимальная версия: ввод улова (вес, длина, фото по URL) → сохранение в SQLite → просмотр.

## Запуск
1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустите сервер:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Откройте в браузере: http://localhost:8000

> База данных `catches.db` создаётся автоматически при первом запуске.


скрины 
<img width="1175" height="857" alt="image" src="https://github.com/user-attachments/assets/39f4f6cb-4b3b-4ecb-bd18-d26386f1d4d7" />
