@echo off
title Momsbebe Dashboard + External Access
cd /d "C:\종목 검색기\momsbebe-dashboard"
echo ============================================
echo   신아인터네셔날 업무 대시보드
echo ============================================
echo.

set CLOUDFLARED=C:\Users\momsb\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe

:: 서버를 백그라운드로 시작
start /min cmd /c "python -m streamlit run app.py --server.headless true --server.port 8501"
timeout /t 4 /nobreak >nul

echo [OK] 서버 시작 완료
echo.
echo   사무실 직원 접속: http://192.168.0.38:8501
echo.
echo [..] 외부 접속 터널 시작 중...
echo     아래에 표시되는 URL을 복사해서 사용하세요.
echo     (https://xxxx-xxxx.trycloudflare.com 형태)
echo.
echo     이 창을 닫으면 외부 접속이 끊깁니다.
echo     최소화 해두세요.
echo.

"%CLOUDFLARED%" tunnel --url http://localhost:8501
pause
