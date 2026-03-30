@echo off
title Momsbebe Dashboard Server
cd /d "C:\종목 검색기\momsbebe-dashboard"
echo ============================================
echo   신아인터네셔날 업무 대시보드 서버 시작
echo   http://localhost:8501
echo ============================================
echo.
echo 이 창을 닫으면 서버가 종료됩니다.
echo 최소화해두면 백그라운드에서 계속 실행됩니다.
echo.
python -m streamlit run app.py --server.headless true --server.port 8501
pause
