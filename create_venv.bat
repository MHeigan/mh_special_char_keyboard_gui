@echo off
setlocal
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
if exist requirements.txt (
  pip install -r requirements.txt
)
echo.
echo Virtual environment ready. To activate later:
echo   call .venv\Scripts\activate
