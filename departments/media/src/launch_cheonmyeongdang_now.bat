@echo off
REM 천명당 정식 오픈 단발 발송 — 모든 활성 채널 (7채널)
REM 사용: 더블클릭 또는 cmd에서 실행

setlocal
set PY=python
set SRC=D:\cheonmyeongdang\departments\media\src
set LOG=D:\cheonmyeongdang\departments\media\logs\launch_cheon.log

cd /d %SRC%
echo === 천명당 정식 오픈 단발 발송 시작 ===
%PY% may_promo_runner.py --launch-cheon
echo === 완료. 로그: %LOG% ===

endlocal
pause
