@echo off
schtasks /Run /TN "KunStudio_Sales"
timeout /t 2 /nobreak > nul
schtasks /Run /TN "KunStudio_Security"
timeout /t 2 /nobreak > nul
schtasks /Run /TN "KunStudio_Pinterest_4Lang_Daily"
timeout /t 2 /nobreak > nul
schtasks /Run /TN "Cheonmyeongdang_PayPal_Daily_Monitor"
timeout /t 2 /nobreak > nul
schtasks /Run /TN "KunStudio_Contests"
timeout /t 2 /nobreak > nul
schtasks /Run /TN "KunStudio_DevTo_Daily"
timeout /t 2 /nobreak > nul
schtasks /Run /TN "KunStudio_Influencer_Reply_Monitor"
echo DONE
