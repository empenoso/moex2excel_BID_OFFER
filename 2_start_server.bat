@echo off
chcp 65001 >nul
title Tinkoff XML API Server

echo Запуск сервера FastAPI через Uvicorn...
echo.
echo (закройте это окно, чтобы остановить сервер)
echo.
echo Михаил Шардин https://shardin.name/
echo.
echo.

uvicorn server:app --host 127.0.0.1 --port 8000
pause
