@echo off
echo Starte Backend...
start cmd /k "cd /d ""C:\Users\Miguel\Projects\Sociel Meidia Auto Posting App\backend"" && python main.py"

echo Starte Frontend...
start cmd /k "cd /d ""C:\Users\Miguel\Projects\Sociel Meidia Auto Posting App\frontend"" && npm run dev -- -p 3001"

echo Warte kurz auf das Frontend...
timeout /t 5 >nul

echo Starte Tunnel...
start cmd /k "npx localtunnel --port 3001 --subdomain autoshorts-mimaros"

echo Alles gestartet!
echo Bitte oeffne: https://autoshorts-mimaros.loca.lt
