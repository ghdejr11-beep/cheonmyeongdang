@echo off
setlocal
set PY=C:\Users\hdh02\AppData\Local\Programs\Python\Python311\python.exe

schtasks /Change /TN "KunStudio_Sales" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\intelligence\sales_collector.py\""
schtasks /Change /TN "KunStudio_Security" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\security\security_audit.py\""
schtasks /Change /TN "KunStudio_Influencer_Reply_Monitor" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\secretary\monitor_influencer_replies.py\""
schtasks /Change /TN "KunStudio_Pinterest_4Lang_Daily" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\pinterest_pins\publish_one_queued.py\""
schtasks /Change /TN "KunStudio_DevTo_Daily" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\devto_crosspost\publish.py\""
schtasks /Change /TN "KunStudio_Contests" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\intelligence\contests_watch.py\""
schtasks /Change /TN "Cheonmyeongdang_PayPal_Daily_Monitor" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\sales-collection\paypal_daily_monitor.py\""
schtasks /Change /TN "KunStudio_B2B_Outreach_Daily" /TR "\"%PY%\" -X utf8 \"D:\scripts\b2b_outreach_packet.py\""
schtasks /Change /TN "KunStudio_Autopilot_Hourly" /TR "\"%PY%\" -X utf8 \"D:\scripts\autopilot_hourly.py\""
schtasks /Change /TN "KunStudio_Autopilot_Daily" /TR "\"%PY%\" -X utf8 \"D:\scripts\autopilot_daily.py\""
schtasks /Change /TN "KunStudio_Autopilot_Weekly" /TR "\"%PY%\" -X utf8 \"D:\scripts\autopilot_weekly.py\""
schtasks /Change /TN "KunStudio_AdobeStockBatch" /TR "\"%PY%\" -X utf8 \"D:\scripts\adobe_stock_korean_batch.py\" --all --count-per-niche 3"
schtasks /Change /TN "KunStudio_SupportQueue" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\ceo-briefing\support_agent.py\" process"
schtasks /Change /TN "KunStudio_CmdViral_12" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\media\post_cheonmyeongdang_viral.py\""
schtasks /Change /TN "KunStudio_CmdViral_15" /TR "\"%PY%\" -X utf8 \"D:\cheonmyeongdang\departments\media\post_cheonmyeongdang_viral.py\""

echo ===VERIFY===
schtasks /Query /TN "KunStudio_Sales" /XML | findstr /C:"<Command>" /C:"<Arguments>"
echo DONE
