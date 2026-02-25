@echo off
title AI 日報檢視器 - 本地伺服器
echo =========================================================
echo 正在啟動「食品加工 AI 新技術日報」本地檢視器...
echo =========================================================
echo.
echo 注意事項：
echo 1. 請勿關閉此黑灰色視窗，否則網頁將無法運作。
echo 2. 檢視完畢後再關閉此視窗。
echo.

cd /d "%~dp0docs"
start http://localhost:8000
python -m http.server 8000

echo.
pause
