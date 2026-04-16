# KDP 책 생성 규칙 (편집부 SOP)

**중요:** 새 책을 generate.py 또는 cover 생성 스크립트에 추가할 때 이 규칙을 반드시 따를 것.

## 🚨 과거 거절 이력 (2026-04-14)

6권 거절됨 → 다음 규칙 생성

---

## 📕 표지 규칙 (Cover)

### 필수 제거 항목
- ❌ **"ISBN Barcode Area" 텍스트 금지** — KDP가 자동으로 바코드 넣어줌
- ❌ **회색 사각형 placeholder 박스 금지**
- ❌ **템플릿 가이드선/도움말 텍스트 일체 금지**
- ❌ **"Cover Template" / "Print Area" 같은 안내 문구 금지**

### Spine (책등) 규칙
- ✅ **상하 여백 최소 0.375인치 (9.6mm)** — 안전하게 **0.5인치 권장**
- ✅ 페이지 수가 79쪽 이상이어야 spine 텍스트 가능 (미만이면 제목만)
- ✅ Spine 폰트 크기: 최대 11pt, 최소 5pt
- ✅ Spine 텍스트: 세로 방향 (90도 회전)

### 저자명 규칙
- ✅ **모든 책 저자명 통일: `Deokgu Studio`**
- ✅ KDP 설정 단계에서 입력한 저자명과 **표지/백커버/스파인 모두 일치**해야 함
- ❌ generate.py와 cover 생성기의 저자명이 다르면 거절됨

### 본문 규칙 (Interior)
- ✅ 최소 폰트 크기: **7pt**
- ✅ 이미지 해상도: **300dpi 이상**
- ✅ 마진: 최소 0.375인치 (내측은 0.5~0.75인치 권장)
- ✅ 텍스트 대비: 배경과 충분히 구분되어야 함 (흐림/픽셀화 금지)

---

## 📝 메타데이터 규칙

### Low-Content Book 체크
활동북/플래너/저널 등은 반드시 **Low-content book 체크박스 ON**
- Dot Marker Book → Low-content ✅
- Sleep Planner → Low-content ✅
- Password Logbook → Low-content ✅
- Coloring Book → Low-content ✅
- Spot the Difference → Low-content ✅

체크 시 **ISBN 선택 옵션 변경** (Amazon 무료 ISBN 사용)

### Regular Content Book
일반 서적 (텍스트 위주) → Low-content 체크 **안 함**
- AI Side Hustle Blueprint → Regular
- Workbook with text → Regular

---

## 🆔 신원인증

- KDP 계정은 **신원인증 필수**
- 정부 발급 신분증 (주민등록증, 여권, 운전면허증)
- 미인증 시 **계정 정지** → 출판 불가
- 보통 1년에 1회 갱신 요청 옴

---

## ✅ 책 생성 체크리스트

새 책 생성 전:
- [ ] 표지에 "ISBN Barcode Area" 문구 없음
- [ ] 회색 placeholder 박스 없음
- [ ] Spine 상하 여백 0.5인치 이상
- [ ] 저자명 "Deokgu Studio"로 통일
- [ ] 본문 폰트 7pt 이상
- [ ] 이미지 300dpi 이상
- [ ] Low-content 여부 판단 (활동북이면 ON)

KDP 업로드 시:
- [ ] 표지 업로드 (cover.pdf)
- [ ] 본문 업로드 (Interior.pdf)
- [ ] 메타데이터 확인 (제목, 저자, 설명, 카테고리)
- [ ] **Low-content 체크박스 확인**
- [ ] ISBN 옵션 확인 (Amazon 무료 vs 자체)
- [ ] 가격 설정
- [ ] Preview로 최종 확인

---

## 🔧 사용 스크립트

| 목적 | 스크립트 |
|------|---------|
| 모든 책 본문 재생성 | `projects/*/generate.py` |
| 모든 책 마진/표지 수정 | `projects/fix_all_margins_and_covers.py` |
| 거절된 책만 표지 재생성 | `projects/regenerate_rejected_covers.py` |
| 전체 표지 생성 | `projects/generate_all_covers.py` |

---

**이 문서는 편집부 공식 SOP입니다. 새 책 추가 시 반드시 따르세요.**
