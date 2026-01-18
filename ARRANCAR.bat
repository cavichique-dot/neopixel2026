@echo off
cd /d "C:\Users\carlo\AdSellPro"
echo.
echo ========================================
echo    AdSell Pro - NPIXEL 2026
echo ========================================
echo.
echo ACTIVANDO ENTORNO...
call venv\Scripts\activate

echo.
echo ¡¡¡ SISTEMA FULL CARGANDO !!!
echo.
python run.py
echo INSTALANDO LAS LIBRERÍAS FALTANTES...
pip install --upgrade qrcode[pil] pillow weasyprint
echo.
echo === LISTO, JEFE ===
echo.
pause