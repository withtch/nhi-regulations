@echo off
chcp 65001 > nul
echo --------------------------------------------------
echo 🔄 1. 正在強制終止背景運行的 Streamlit 與 Python 程序...
echo --------------------------------------------------
taskkill /F /IM python.exe /T 2>nul

echo.
echo --------------------------------------------------
echo 🧹 2. 正在清理舊資料庫與對照表...
echo --------------------------------------------------
if exist nhi_rules.db del /f /q nhi_rules.db
if exist drug_mapping.json del /f /q drug_mapping.json

echo.
echo --------------------------------------------------
echo ⚙️ 3. 執行資料庫精準區塊切割 (build_db.py)...
echo --------------------------------------------------
python build_db.py

echo.
echo --------------------------------------------------
echo 📚 4. 生成全藥品章節對照字典 (generate_mapping.py)...
echo --------------------------------------------------
python generate_mapping.py

echo.
echo --------------------------------------------------
echo 🚀 5. 重新啟動 Streamlit 服務 (app.py)...
echo --------------------------------------------------
streamlit run app.py
pause