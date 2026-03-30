@echo off
echo ============================================
echo   대시보드 서버 자동시작 등록
echo ============================================
echo.

set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_SRC=C:\종목 검색기\momsbebe-dashboard\start_server_bg.vbs

if exist "%STARTUP%\momsbebe_dashboard.vbs" (
    echo 이미 등록되어 있습니다.
) else (
    copy "%VBS_SRC%" "%STARTUP%\momsbebe_dashboard.vbs"
    echo 등록 완료! PC 재시작 시 자동으로 서버가 시작됩니다.
)
echo.
echo 제거하려면: del "%STARTUP%\momsbebe_dashboard.vbs"
echo.
pause
