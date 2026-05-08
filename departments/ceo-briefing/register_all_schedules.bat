@echo off
chcp 65001 >nul
REM Kunstudio all-in-one schedule registrar (UTF-8 safe)

echo.
echo [1/7] Daily revenue report at 09:00
schtasks /Create /TN "KunStudio_RevenueReport" /TR "python -X utf8 D:\cheonmyeongdang\departments\ceo-briefing\revenue_report.py" /SC DAILY /ST 09:00 /F

echo.
echo [2/7] Daily intelligence scan at 00:30
schtasks /Create /TN "KunStudio_Intelligence" /TR "python -X utf8 D:\cheonmyeongdang\departments\intelligence\watch.py all" /SC DAILY /ST 00:30 /F

echo.
echo [3/7] Support queue every 10 minutes
schtasks /Create /TN "KunStudio_SupportQueue" /TR "python -X utf8 D:\cheonmyeongdang\departments\ceo-briefing\support_agent.py process" /SC MINUTE /MO 10 /F

echo.
echo [4/7] Telegram bot on logon
schtasks /Create /TN "KunStudio_TelegramBot" /TR "python -X utf8 D:\cheonmyeongdang\departments\ceo-briefing\telegram_bot.py" /SC ONLOGON /F

echo.
echo [5/7] Contest watch daily at 09:05 (지원가능 공모전 발굴)
schtasks /Create /TN "KunStudio_Contests" /TR "python -X utf8 D:\cheonmyeongdang\departments\intelligence\contests_watch.py" /SC DAILY /ST 09:05 /F

echo.
echo [6/7] Service health check every 5 minutes (KORLENS + 세금N혜택)
schtasks /Create /TN "KunStudio_HealthCheck" /TR "python -X utf8 D:\cheonmyeongdang\departments\intelligence\health_check.py" /SC MINUTE /MO 5 /F

echo.
echo [7/7] Daily sales report at 10:00 + Security audit 03:00 + Intrusion watch 5min
schtasks /Create /TN "KunStudio_Sales" /TR "python -X utf8 D:\cheonmyeongdang\departments\intelligence\sales_collector.py" /SC DAILY /ST 10:00 /F
schtasks /Create /TN "KunStudio_Security" /TR "python -X utf8 D:\cheonmyeongdang\departments\security\security_audit.py" /SC DAILY /ST 03:00 /F
schtasks /Create /TN "KunStudio_Intrusion" /TR "python -X utf8 D:\cheonmyeongdang\departments\security\intrusion_watch.py" /SC MINUTE /MO 5 /F

echo.
echo [+1] Unified media poster every 10 minutes (TG + X + IG + Kakao + LINE)
schtasks /Create /TN "KunStudio_MediaPoster" /TR "python -X utf8 D:\cheonmyeongdang\departments\media\scheduler\unified_poster.py" /SC MINUTE /MO 10 /F

echo.
echo [+2] Daily auto promo AM 10:00 (weekday rotation — KORLENS·천명당·세금·보험)
schtasks /Create /TN "KunStudio_AutoPromo_AM" /TR "python -X utf8 D:\cheonmyeongdang\departments\media\src\auto_promo.py daily" /SC DAILY /ST 10:00 /F

echo.
echo [+3] Daily auto promo PM 20:00 (저녁 재포스팅)
schtasks /Create /TN "KunStudio_AutoPromo_PM" /TR "python -X utf8 D:\cheonmyeongdang\departments\media\src\auto_promo.py daily" /SC DAILY /ST 20:00 /F

echo.
echo [+4] Weekly summary Sunday PM 9:00
schtasks /Create /TN "KunStudio_WeeklySummary" /TR "python -X utf8 D:\cheonmyeongdang\departments\media\src\auto_promo.py weekly" /SC WEEKLY /D SUN /ST 21:00 /F

echo.
echo === Registered tasks ===
schtasks /Query /TN "KunStudio_RevenueReport"
schtasks /Query /TN "KunStudio_Intelligence"
schtasks /Query /TN "KunStudio_SupportQueue"
schtasks /Query /TN "KunStudio_TelegramBot"
schtasks /Query /TN "KunStudio_Contests"
schtasks /Query /TN "KunStudio_HealthCheck"
schtasks /Query /TN "KunStudio_Sales"
schtasks /Query /TN "KunStudio_Security"
schtasks /Query /TN "KunStudio_Intrusion"
schtasks /Query /TN "KunStudio_MediaPoster"
schtasks /Query /TN "KunStudio_AutoPromo_AM"
schtasks /Query /TN "KunStudio_AutoPromo_PM"
schtasks /Query /TN "KunStudio_WeeklySummary"

echo.
echo All done.
pause
