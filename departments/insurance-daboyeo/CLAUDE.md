# 🛡️ 보험다보여팀 (Insurance Daboyeo Division)

> **보험 통합 관리 AI 앱 — 한국 전용**
> 금감원·복지부 API 연동하여 가입 보험 자동 조회 + 건강분석 기반 심사 예측.

## 📍 기본 정보

- **코드명**: `insurance-daboyeo`
- **타겟**: 🇰🇷 한국 전용
- **언어**: 한국어
- **수익 모델**: 설계사 제휴 수수료 + 광고 + 프리미엄 기능
- **수익 우선순위**: 5순위 (심사 통과 전까지 랭킹 제외)
- **총괄팀장**: `gm-insurance-daboyeo`
- **현재 상태**: 프로토타입 완료 + 정부 API 심사 대기

## 📱 앱 현황

**파일명:** `insurance_app.html`
**위치:** 현재 CEO 로컬 `C:\Users\hdh02\Desktop` (리포로 이사 필요)

### 구현된 7개 탭
1. **보험사 연동 탭** — 생명보험사 22개 + 손해보험사 12개 (총 34개사)
2. **내보험다보여 API** — 금감원 `fine.fss.or.kr` 연동 설계
3. **마이헬스웨이 API** — 복지부 `myhealthway.go.kr` 심평원 5년 진료기록
4. **🏥 가입 전 건강분석** — 진료기록 타임라인, 고지의무 체크, 심사 통과율 예측
5. **약관 연결** — 생보협회(klia.or.kr) / 손보협회(knia.or.kr) 공시실 PDF 직접 연결
6. **설계사 연결** — GA 소속 설계사 프로필 (정보 표시만, 채팅/예약 제거됨)
7. **기타** — 맞춤 추천 AI, 보험료 계산기, 갱신·만기 알림, 수동 입력

상세: `docs/features.md` 참고.

## 👥 하위팀 (3팀)

| 팀 | 코드 | 담당 |
|---|---|---|
| 앱개발팀 | `lead-insurance-app` | `insurance_app.html` 모듈화, 배포 (Vercel) |
| API심사·연동팀 | `lead-insurance-api` | 금감원·복지부 심사 서류, 연동 구현 |
| 사업개발팀 | `lead-insurance-biz` | 수익 모델, GA 제휴, 설계사 영업 |

## 🔴 핵심 병목

1. **금감원 심사** (3~5일): 사업자등록증 + 개인정보 처리방침 URL 제출
2. **마이헬스웨이 심사** (5~10일): 카카오·PASS·공동인증서 본인 인증 체인
3. **수익 모델 미확정**: 설계사 연결 탭은 정보만 표시, 수수료 경로 없음

## 📂 폴더 구조

```
insurance-daboyeo/
├── CLAUDE.md              (이 파일)
├── revenue.md
├── roadmap.md
├── status.md              (심사 진행 DD-day)
├── docs/
│   └── features.md        (7개 탭 명세)
├── app/                   (앱개발팀)
│   └── insurance_app.html (CEO 업로드 필요)
├── api-integration/       (API심사·연동팀)
│   ├── fss-application/   (금감원 서류)
│   └── myhealthway/       (복지부 서류)
└── business/              (사업개발팀)
    ├── revenue-model.md
    └── ga-partnerships.md
```

## 🔑 필요한 도구 (심사 후)

- `FSS_INSTITUTION_CODE`, `FSS_API_KEY` — 금감원
- `MYHEALTHWAY_API_KEY` — 마이헬스웨이
- `TOSS_SECRET_KEY`, `KAKAOPAY_CID` — 결제
- 크롤링 (WebFetch) — 34개 보험사 상품 업데이트

## ⚠️ 법적·규제 주의사항

- 건강정보는 **민감정보**. GDPR·개인정보보호법 엄격 준수.
- 금융상품 비교 서비스는 **금융소비자보호법** 해당.
- 설계사 연결은 **유상 광고**로 표시 필수.
- 심사 통과 전 **실제 사용자에게 API 데이터 노출 금지**.
