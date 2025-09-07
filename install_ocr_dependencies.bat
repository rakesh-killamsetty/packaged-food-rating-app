@echo off
echo Installing OCR and Barcode Detection Dependencies...
echo.

echo Installing basic dependencies...
pip install pillow opencv-python numpy

echo.
echo Installing OCR libraries...
pip install easyocr pytesseract

echo.
echo Installing barcode detection...
pip install pyzbar

echo.
echo Installing additional dependencies...
pip install anthropic openai

echo.
echo Installation complete!
echo.
echo Note: For pytesseract to work, you may need to install Tesseract OCR:
echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo.
pause
