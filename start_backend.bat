@echo off
echo Starting Universal Cultural Intelligence System...

REM Navigate to backend directory
cd /d "C:\Users\kaz.roche\Desktop\music-intelligence\backend"

REM Check if virtual environment exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install required packages (only if needed)
echo Installing/checking dependencies...
pip install flask flask-cors requests python-dotenv pyjwt

REM Start the server
echo Starting Cultural Intelligence Server...
python simple_working.py

pause