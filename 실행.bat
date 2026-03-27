@echo off
chcp 65001 >nul
echo ==========================================
echo   사주멘토 - 사주도 풀고, 내 마음도 풀고
echo ==========================================
echo.

cd /d "%~dp0"
start /B python app.py
timeout /t 2 >nul
start http://localhost:5031

echo 서버가 실행 중입니다 (http://localhost:5031)
echo 종료하려면 아무 키나 누르세요...
pause >nul

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5031 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
