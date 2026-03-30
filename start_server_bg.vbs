Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d ""C:\종목 검색기\momsbebe-dashboard"" && python -m streamlit run app.py --server.headless true --server.port 8501", 0, False
Set WshShell = Nothing
