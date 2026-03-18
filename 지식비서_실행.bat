@echo off
echo ==========================================
echo  EASYSAFE 지식 비서 웹 서비스 시작 중...
echo ==========================================
echo.
echo 1. 서버 구동 중...
start /b python server.py
echo 2. 잠시만 기다려 주세요 (3초)...
timeout /t 3 /nobreak > nul
echo 3. 브라우저에서 서비스 실행 중: http://localhost:8001
start http://localhost:8001
echo.
echo ==========================================
echo  서버를 종료하려면 이 창을 닫으세요.
echo ==========================================
pause
