@echo off
set mypath=%~dp0
pyinstaller --onefile --noconsole %mypath%GeyserPredictions.py
pause
