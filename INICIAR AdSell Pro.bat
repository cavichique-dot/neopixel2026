@echo off
echo.
echo ========================================
echo    AdSell Pro - NPIXEL 2026
echo ========================================
echo ACTIVANDO ENTORNO...
echo SISTEMA FULL CARGANDO !!!
echo ========================================
echo.
cd /d %~dp0
call venv\Scripts\activate
python start.py
echo.
echo ════════════════════════════════════════
echo   SISTEMA CERRADO - HASTA LA PROXIMA JEFE
echo ════════════════════════════════════════
pause