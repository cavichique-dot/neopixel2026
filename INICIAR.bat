@echo off
cd /d "C:\Users\carlo\AdSellPro"

if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate

pip install --upgrade pip --no-cache-dir
pip install flask flask-login flask-sqlalchemy pdfkit qrcode[pil] pandas pyyaml --no-cache-dir

echo.
echo ¡SISTEMA FULL LISTO SIN WEASYPRINT!
python run.py
pause