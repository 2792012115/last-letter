@echo off
echo ========================================
echo    AI 最后一封信 - 公网部署工具
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] 未找到 Python，请先安装
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 安装依赖...
pip install flask openai python-dotenv -q

REM 检查 ngrok
where ngrok >nul 2>&1
if errorlevel 1 (
    echo [2/3] ngrok 未安装，正在下载...
    curl -L https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip -o ngrok.zip
    tar -xf ngrok.zip
    del ngrok.zip
    echo ngrok 已下载到当前目录
) else (
    echo [2/3] ngrok 已安装
)

echo.
echo [3/3] 启动服务...
echo.
echo 请先在一个新的终端窗口运行:
echo   cd "c:\Users\27920\OneDrive\Desktop\希望能通过\last-letter"
echo   python web_app.py
echo.
echo 然后在另一个终端运行:
echo   ngrok http 5000
echo.
echo ngrok 会给你一个公网地址，把它填入 miniapp/app.js 即可！
echo ========================================
pause
