# Play Console v1.3.1 AAB 업로드 — 5분 → 3분 원샷 가이드

**파일**: `D:\cheonmyeongdang\android\app\build\outputs\bundle\release\app-release.aab` (12.36 MB, 2026-05-07 13:05 빌드 완료)

## 1클릭 직링크
- 프로덕션 출시 페이지: https://play.google.com/console/u/0/developers/9082303253289895857/app-list
  (앱 선택 → "프로덕션" → "새 버전 만들기")
- 또는 직접 앱: https://play.google.com/console (천명당 앱 → 프로덕션 트랙)

## 7단계 클릭 순서

1. **앱 선택** → 좌측 메뉴 "프로덕션(Production)" 클릭
2. **"새 버전 만들기"** 버튼 클릭 (우측 상단 파란 버튼)
3. **App Bundle 업로드**: "업로드" 버튼 → 위 AAB 경로 그대로 paste/drop
   - 버전 코드: 자동 (이전 +1)
   - 버전 이름: `1.3.1`
4. **출시 노트**: 4개 언어 칸에 아래 텍스트 그대로 paste
5. **출시 비율 (Rollout)**: "단계적 출시" → **20%** 입력
6. **저장 → 검토 → 프로덕션 출시 시작** 클릭
7. 검토 제출 완료 페이지 캡처

## 출시 노트 (4 lang, 각 500자 이내)

### 한국어 (ko-KR)
```
v1.3.1 — 4 언어 글로벌 라이브
• 한국어/English/日本語/中文 4 언어 동시 지원
• 매직링크 OTP 로그인 (이메일 1클릭)
• AI Q&A 챗봇 24시간 (본인 사주 grounding)
• 월별 PDF 30페이지 리포트 (매월 1일 자동)
• 시각화 차트 4종 (오행 레이더/대운 곡선/궁합 매트릭스/월운 히트맵)
• 안정성 개선 및 버그 수정
```

### English (en-US)
```
v1.3.1 — 4-Language Global Release
• Korean / English / Japanese / Chinese — 4 languages live
• Magic-link OTP login (one-click email)
• 24/7 AI Q&A chatbot grounded on your 4-pillar chart
• Monthly 30-page PDF report (auto every 1st)
• 4 new visualization charts (5-element radar / luck-curve / compatibility matrix / monthly heatmap)
• Stability improvements and bug fixes
```

### 日本語 (ja-JP)
```
v1.3.1 — 4言語グローバル対応
• 韓国語 / English / 日本語 / 中文の4言語に対応
• マジックリンクOTPログイン (メール1クリック)
• 24時間AI Q&Aチャット (本人の四柱に基づく回答)
• 毎月30ページのPDFレポート (毎月1日自動配信)
• ビジュアライゼーション4種(五行レーダー/大運曲線/相性マトリクス/月運ヒートマップ)
• 安定性向上およびバグ修正
```

### 中文 (zh-CN)
```
v1.3.1 — 4语言全球版上线
• 韩语 / English / 日本语 / 中文四语言同步支持
• 魔法链接OTP登录(邮箱一键)
• 24小时AI问答聊天(基于本人四柱命盘)
• 每月30页PDF运势报告(每月1日自动)
• 4种可视化图表(五行雷达/大运曲线/合婚矩阵/月运热力图)
• 稳定性改进及问题修复
```

## 단계적 출시(Rollout) 권장
- **20%** — v1.3 안정성 검증 후 24시간 내 100% 확장 권장
- 크래시율 1% 미만 유지 시 자동 100% 가능

## 검토 ETA
- 일반 출시: 1~3시간 (24시간 내 99%)
- 정책 검토 트리거되면 1~3일

---
**예상 사용자 시간: 3분 (페이지 진입 30초 + AAB 드래그 30초 + 4 lang paste 90초 + Rollout 20% 입력 + 출시 클릭 30초)**
