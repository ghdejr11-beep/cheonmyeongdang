# 🛡️ 보험다보여팀 — 진행 상황 대시보드

> 매일 09:00 KST 업데이트.

## 🔴 가장 큰 병목

**정부 API 심사** — 심사 신청 전 단계.

## 📋 심사 진행 상황

### 1. 금감원 (내보험다보여)
- **URL**: https://fine.fss.or.kr
- **상태**: ⏸️ 미신청
- **제출 필요 서류**:
  - [ ] 사업자등록증 사본
  - [ ] 개인정보 처리방침 URL
  - [ ] 서비스 소개서
  - [ ] 법인 인증서
- **예상 심사 기간**: 3~5일
- **발급 예정**: 기관코드 + API Key

### 2. 복지부 (마이헬스웨이)
- **URL**: https://myhealthway.go.kr
- **상태**: ⏸️ 미신청
- **인증 체인**: 카카오/PASS/공동인증서 → 건강보험공단 → 심평원 (5단계)
- **제출 필요 서류**:
  - [ ] 사업자등록증
  - [ ] 개인정보 처리방침
  - [ ] 서비스 이용 흐름도
  - [ ] 보안 조치 명세
- **예상 심사 기간**: 5~10일
- **발급 예정**: API Key (심평원 5년 진료기록 조회용)

## 📱 앱 파일 상태

- **위치**: CEO 로컬 `C:\Users\hdh02\Desktop\insurance_app.html`
- **리포 이사**: ⏸️ 대기 중 (CEO 업로드 필요)
- **업로드 경로**: `departments/insurance-daboyeo/app/insurance_app.html`

### 업로드 방법 (추천)
1. GitHub 웹 `ghdejr11-beep/cheonmyeongdang` 접속
2. 브랜치: `claude/video-integration-tools-iDNak`
3. `departments/insurance-daboyeo/app/` 이동
4. "Add file" → "Upload files" → 드래그 앤 드롭

## 🗓️ D-Day 카운트다운

| 항목 | 목표일 | D-Day |
|---|---|---|
| 금감원 서류 제출 | — | — |
| 마이헬스웨이 서류 제출 | — | — |
| 금감원 API 키 발급 | — | — |
| 마이헬스웨이 API 키 발급 | — | — |
| 베타 오픈 | — | — |
| 정식 오픈 | — | — |

## ⚠️ 현재 블로커

1. `insurance_app.html` 리포에 아직 없음
2. 사업자등록증 필요 (법인 / 개인사업자 여부 확인)
3. 개인정보 처리방침 문서 없음
