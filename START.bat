@echo off
title KI Uebersetzer
cd /d "%~dp0"

echo.
echo  Starte KI Uebersetzer...
echo.

REM API-Key aus .env laden
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="ANTHROPIC_API_KEY" set ANTHROPIC_API_KEY=%%b
)

REM Lokale IP ermitteln
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "169.254"') do (
    set LOCAL_IP=%%a
    goto :found_ip
)
:found_ip
set LOCAL_IP=%LOCAL_IP: =%

echo  ==========================================
echo   KI Uebersetzer laeuft!
echo  ==========================================
echo   PC:    http://localhost:5003
echo   Handy: http://%LOCAL_IP%:5003
echo  ==========================================
echo.
echo   Handy muss im selben WLAN sein!
echo   Zum Beenden: Strg+C oder Fenster schliessen
echo.

"C:\Users\retti\AppData\Local\Python\bin\python.exe" app.py

echo.
echo  Server beendet.
pause
