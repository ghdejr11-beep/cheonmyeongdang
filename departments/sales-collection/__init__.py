"""
sales-collection 부서 — 매출/트래픽 데이터 수집 전담

모듈:
- admob_collector.py / admob_auth_setup.py — AdMob 광고 매출 (1번 agent 담당)
- yt_dashboard.py — 4채널 YouTube 통합 분석 (Healing Sleep Realm /
  Whisper Atlas / Wealth Blueprint / Inner Archetypes)
- yt_channel_map.json — 채널 핸들 → channelId 매핑
- gumroad_collector.py — Gumroad API v2 (디지털 상품 매출)
- kdp_scraper.py — Amazon KDP Playwright 스크래핑 (옵트인, ToS 회색지대)
- kreatie_manual.py — 크티 수동 입력 CLI
- unified_revenue.py — 5개 채널 통합 (어제/7일/30일 + 환산 KRW)
- data/{admob,yt_4ch,gumroad,kdp,kreatie_manual,unified_revenue}_daily.json
"""
