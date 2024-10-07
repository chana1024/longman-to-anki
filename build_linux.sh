#!/bin/bash
pyinstaller --onefile --add-data "dist:dist" longmanToAnki.py
mv dist/longmanToAnki .
rm -rf build __pycache__ longmanToAnki.spec