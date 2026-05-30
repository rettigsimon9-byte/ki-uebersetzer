# KI Übersetzer starten
# -------------------------------------------------------
# Holt die lokale IP-Adresse, damit du die App auch vom
# Handy im selben WLAN öffnen kannst.

$python = "C:\Users\retti\AppData\Local\Python\bin\python.exe"

# Dependencies installieren (nur beim ersten Mal nötig)
& $python -m pip install -r requirements.txt -q

# API-Key aus .env laden
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.+)$') {
        [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
    }
}

# Lokale IP ausgeben
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' -and $_.IPAddress -notmatch '^169' } | Select-Object -First 1).IPAddress

Write-Host ""
Write-Host "  ╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       KI Übersetzer gestartet        ║" -ForegroundColor Cyan
Write-Host "  ╠══════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "  ║  PC:    http://localhost:5003         ║" -ForegroundColor Green
Write-Host "  ║  Handy: http://${ip}:5003         ║" -ForegroundColor Yellow
Write-Host "  ╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  → Handy-URL im selben WLAN öffnen!" -ForegroundColor Yellow
Write-Host "  → Zum Beenden: Strg+C" -ForegroundColor Gray
Write-Host ""

& $python app.py
