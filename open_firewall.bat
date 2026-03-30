@echo off
echo ============================================
echo   대시보드 방화벽 포트 개방 (8501)
echo   관리자 권한이 필요합니다
echo ============================================
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 관리자 권한으로 다시 실행해주세요.
    echo     이 파일을 우클릭 - 관리자 권한으로 실행
    pause
    exit /b
)

netsh advfirewall firewall add rule name="Momsbebe Dashboard (TCP 8501)" dir=in action=allow protocol=TCP localport=8501
echo.
echo [OK] 방화벽 규칙 추가 완료!
echo 같은 네트워크의 다른 PC에서 접속 가능합니다.
echo.
pause
