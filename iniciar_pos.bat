@echo off
REM =====================================================================
REM Lanzador del Punto de Venta para Dulcería (Windows XP / 7 / 10 / 11)
REM =====================================================================

title Punto de Venta - Dulcería
cd /d "%~dp0"

REM 1. Intentar ejecutar con pythonw en PATH (sin ventana negra de consola)
where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pythonw main.py
    exit
)

REM 2. Intentar buscar en las rutas estándar de instalación de Python 3.4
if exist "C:\Python34\pythonw.exe" (
    start "" "C:\Python34\pythonw.exe" main.py
    exit
)

if exist "C:\Python34\python.exe" (
    "C:\Python34\python.exe" main.py
    exit
)

REM 3. Intentar con python normal en PATH
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python main.py
    exit
)

REM 4. Si no se encontró Python, mostrar mensaje de ayuda
cls
echo =====================================================================
echo               PUNTO DE VENTA - DULCERIA
echo =====================================================================
echo.
echo No se encontro Python instalado en esta computadora con Windows.
echo.
echo Para que el sistema funcione en Windows XP:
echo  1. Conecte su memoria USB.
echo  2. Ejecute el instalador oficial: python-3.4.4.msi
echo  3. En la instalacion, asegurese de marcar "Add python.exe to Path"
echo  4. Vuelva a hacer doble clic en este archivo (iniciar_pos.bat)
echo.
echo =====================================================================
pause
