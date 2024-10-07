@echo off
pyinstaller --onefile --add-data "dist;dist" longmanToAnki.py
move dist\longmanToAnki.exe .
rmdir /s /q build
rmdir /s /q __pycache__
del longmanToAnki.spec