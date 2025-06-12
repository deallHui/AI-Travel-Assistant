@echo off
echo Quick Start - RAG AI with Python directly
echo ==========================================

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python 3.9+ first
    pause
    exit /b 1
)

echo Python found, starting RAG AI directly...

:: Go to main directory
cd /d D:\AICD\rag_ai

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install uvicorn fastapi

:: Set environment variables
set DEPLOY_ENV=development
set HOST=0.0.0.0
set PORT=8000

:: Start the API server directly
echo Starting RAG AI API server...
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python backend/public_api.py
