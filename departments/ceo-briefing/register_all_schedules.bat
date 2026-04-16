@echo off
chcp 65001 >nul
REM Kunstudio all-in-one schedule registrar (UTF-8 safe)

echo.
echo [1/4] Daily revenue report at 09:00
schtasks /Create /TN "KunStudio_RevenueReport" /TR "python -X utf8 C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\revenue_report.py" /SC DAILY /ST 09:00 /F

echo.
echo [2/4] Daily intelligence scan at 00:30
schtasks /Create /TN "KunStudio_Intelligence" /TR "python -X utf8 C:\Users\hdh02\Desktop\cheonmyeongdang\departments\intelligence\watch.py all" /SC DAILY /ST 00:30 /F

echo.
echo [3/4] Support queue every 10 minutes
schtasks /Create /TN "KunStudio_SupportQueue" /TR "python -X utf8 C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\support_agent.py process" /SC MINUTE /MO 10 /F

echo.
echo [4/4] Telegram bot on logon
schtasks /Create /TN "KunStudio_TelegramBot" /TR "python -X utf8 C:\Users\hdh02\Desktop\cheonmyeongdang\departments\ceo-briefing\telegram_bot.py" /SC ONLOGON /F

echo.
echo === Registered tasks ===
schtasks /Query /TN "KunStudio_RevenueReport"
schtasks /Query /TN "KunStudio_Intelligence"
schtasks /Query /TN "KunStudio_SupportQueue"
schtasks /Query /TN "KunStudio_TelegramBot"

echo.
echo All done.
pause
