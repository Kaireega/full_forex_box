@echo off
REM Forex Trading System Quick Start Script for Windows
REM This script provides quick commands to start various components of the system

setlocal enabledelayedexpansion

REM Function to display help
if "%1"=="" goto :show_help
if "%1"=="help" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help

REM Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is required but not installed
    exit /b 1
)

REM Main command handling
if "%1"=="setup" goto :setup
if "%1"=="quick-setup" goto :quick_setup
if "%1"=="server" goto :server
if "%1"=="bot" goto :bot
if "%1"=="stream" goto :stream
if "%1"=="all" goto :all
if "%1"=="openai-demo" goto :openai_demo
if "%1"=="test" goto :test
if "%1"=="check" goto :check
if "%1"=="stop" goto :stop
if "%1"=="logs" goto :logs
if "%1"=="install" goto :install

echo [ERROR] Unknown command: %1
echo.
goto :show_help

:show_help
echo.
echo 🚀 Forex Trading System Quick Start
echo.
echo Usage: start.bat [COMMAND]
echo.
echo Commands:
echo   setup         - Full system setup
echo   quick-setup   - Quick setup without demos
echo   server        - Start web server only
echo   bot           - Start trading bot only
echo   stream        - Start data streaming only
echo   all           - Start all services
echo   openai-demo   - Run OpenAI analysis demo
echo   test          - Run test suite
echo   check         - Check system status
echo   stop          - Stop all running services
echo   logs          - Show recent logs
echo   install       - Install dependencies only
echo   help          - Show this help message
echo.
echo Examples:
echo   start.bat setup         # Full system setup
echo   start.bat all           # Start all services
echo   start.bat server        # Start web server only
echo   start.bat check         # Check system status
echo.
goto :end

:setup
echo [INFO] Running full system setup...
python setup.py --all
goto :end

:quick_setup
echo [INFO] Running quick system setup...
python setup.py --quick
goto :end

:server
echo [INFO] Starting web server...
if not exist "server.py" (
    echo [ERROR] server.py not found
    exit /b 1
)
echo [INFO] Web server starting on http://localhost:5000
python server.py
goto :end

:bot
echo [INFO] Starting trading bot...
if not exist "run_bot.py" (
    echo [ERROR] run_bot.py not found
    exit /b 1
)
python run_bot.py
goto :end

:stream
echo [INFO] Starting data streaming...
python -c "import sys; sys.path.append('./'); from stream_example.streamer import run_streamer; run_streamer()"
goto :end

:all
echo [INFO] Starting all services...
echo [INFO] Starting web server...
start /B python server.py
timeout /t 2 /nobreak >nul

echo [INFO] Starting trading bot...
start /B python run_bot.py
timeout /t 2 /nobreak >nul

echo [INFO] Starting data streaming...
start /B python -c "import sys; sys.path.append('./'); from stream_example.streamer import run_streamer; run_streamer()"

echo [INFO] All services started! Press any key to stop all services
pause >nul

echo [INFO] Stopping all services...
taskkill /f /im python.exe /fi "windowtitle eq *server.py*" >nul 2>nul
taskkill /f /im python.exe /fi "windowtitle eq *run_bot.py*" >nul 2>nul
taskkill /f /im python.exe /fi "windowtitle eq *streamer*" >nul 2>nul
echo [INFO] All services stopped
goto :end

:openai_demo
echo [INFO] Running OpenAI analysis demo...
if not defined OPENAI_API_KEY (
    echo [ERROR] OPENAI_API_KEY not set. Set it with:
    echo [ERROR] set OPENAI_API_KEY=your-api-key-here
    exit /b 1
)
if not exist "test_openai_analysis.py" (
    echo [ERROR] test_openai_analysis.py not found
    exit /b 1
)
python test_openai_analysis.py
goto :end

:test
echo [INFO] Running test suite...
if exist "test_openai_analysis.py" (
    echo [INFO] Running OpenAI analysis tests...
    python test_openai_analysis.py
)
if exist "api_tests.py" (
    echo [INFO] Running API tests...
    python api_tests.py
)
if exist "scraping_tests.py" (
    echo [INFO] Running scraping tests...
    python scraping_tests.py
)
echo [INFO] Test suite completed
goto :end

:check
echo [INFO] Checking system status...
echo.
echo 📊 System Status Check
echo.

REM Check if port 5000 is in use (web server)
netstat -an | find ":5000" >nul
if errorlevel 1 (
    echo [WARNING] Web Server: Not running ❌
) else (
    echo [INFO] Web Server: Running on http://localhost:5000 ✅
)

REM Check environment variables
if not defined OPENAI_API_KEY (
    echo [WARNING] OPENAI_API_KEY not set - OpenAI features will be unavailable
    echo [WARNING] Set it with: set OPENAI_API_KEY=your-api-key-here
) else (
    echo [INFO] OPENAI_API_KEY is set ✅
)

REM Check if log directory exists
if exist "logs" (
    for /f %%i in ('dir /b logs 2^>nul ^| find /c /v ""') do set log_count=%%i
    echo [INFO] Log files: !log_count! files in logs/ directory
) else (
    echo [WARNING] Logs directory not found
)

echo.
goto :end

:stop
echo [INFO] Stopping all services...
taskkill /f /im python.exe /fi "windowtitle eq *server.py*" >nul 2>nul
taskkill /f /im python.exe /fi "windowtitle eq *run_bot.py*" >nul 2>nul
taskkill /f /im python.exe /fi "windowtitle eq *streamer*" >nul 2>nul
echo [INFO] All services stopped
goto :end

:logs
echo [INFO] Showing recent logs...
if exist "logs" (
    REM Find the most recent setup log
    for /f "delims=" %%i in ('dir /b /o-d logs\setup_*.log 2^>nul') do (
        set latest_log=%%i
        goto :show_latest_log
    )
    echo [WARNING] No setup logs found
    goto :end
    
    :show_latest_log
    echo [INFO] Latest setup log: logs\!latest_log!
    echo.
    REM Show last 20 lines (Windows doesn't have tail, so we use more with some workaround)
    powershell "Get-Content logs\!latest_log! | Select-Object -Last 20"
) else (
    echo [WARNING] Logs directory not found
)
goto :end

:install
echo [INFO] Installing dependencies...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    exit /b 1
)
python -m pip install -r requirements.txt
echo [INFO] Dependencies installed
goto :end

:end
endlocal