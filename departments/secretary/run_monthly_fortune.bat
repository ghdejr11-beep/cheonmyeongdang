@echo off
set PYTHONIOENCODING=utf-8
cd /d D:\cheonmyeongdang
python departments\secretary\monthly_fortune_send.py >> data\monthly_fortune_log.txt 2>&1
