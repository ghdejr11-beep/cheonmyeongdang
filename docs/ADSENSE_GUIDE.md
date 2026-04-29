# Google AdSense 신청 가이드 — 천명당 (cheonmyeongdang.vercel.app)

> 이 가이드는 천명당 사이트에 Google AdSense 광고를 게재하기 위한 단계별 절차입니다.
> 코드 측 작업(슬롯 6곳 삽입, ads.txt, 메타태그)은 이미 완료된 상태입니다.

---

## 사전 점검 (신청 전 필수)

```bash
cd C:/Users/hdh02/Desktop/cheonmyeongdang
python scripts/adsense_precheck.py
```

모든 항목 PASS 가 나와야 다음 단계로 진행합니다. FAIL 항목은 README 의 안내대로 보완하세요.

---

## Step 1. AdSense 가입

1. https://adsense.google.com 접속
2. **시작하기** 클릭
3. Google 계정으로 로그인 (사이트와 동일 계정 권장)
4. 입력 항목:
   - 웹사이트 URL: `https://cheonmyeongdang.vercel.app`
   - 국가/지역: **대한민국**
   - 약관 동의 체크
5. **계정 만들기** 클릭

### 한국 거주자 추가 정보
- **계좌 정보**: 한국 시중은행 계좌 (KB/신한/우리/하나/IBK 등) — SWIFT 코드 자동 인식
- **주소**: 사업자등록증과 동일한 주소 (쿤스튜디오 사업자등록 주소)
- **이름**: 한글 또는 영문 (Hong Deokhoon / 홍덕훈) — 계좌 예금주명과 정확히 일치
- **세금 정보**: 사업자번호 입력 (간이과세 대상)
- **PIN 우편 인증**: 수익 $10 누적 후 우편으로 발송됨 (약 2~4주)

---

## Step 2. 사이트 추가

1. AdSense 콘솔 → **사이트** 메뉴
2. **사이트 추가** 클릭
3. URL 입력: `cheonmyeongdang.vercel.app` (https:// 제외)
4. **저장** 클릭

이 시점에서 사이트 상태는 **검토 중** (Pending review).

---

## Step 3. AdSense 코드 헤드 삽입 (이미 완료됨)

`index.html` 의 `<head>` 섹션에 이미 다음 코드가 들어있습니다:

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-PLACEHOLDER" crossorigin="anonymous"></script>
```

승인 후 Step 7 에서 `ca-pub-PLACEHOLDER` 자리를 자동 교체합니다.

---

## Step 4. 광고 단위 6개 만들기

승인 후 AdSense 콘솔에서 **광고 → 광고 단위 → 광고 단위 만들기** 로 6개를 생성하세요.

| # | 광고 위치 | 권장 형식 | 코드 내 PLACEHOLDER |
|---|----------|----------|------------------|
| 1 | 사주 결과 하단 | 디스플레이 (자동) | `data-ad-slot="0000000001"` |
| 2 | 궁합 결과 하단 | 디스플레이 (자동) | `data-ad-slot="0000000002"` |
| 3 | 타로 결과 하단 | 디스플레이 (자동) | `data-ad-slot="0000000003"` |
| 4 | 별자리 운세 하단 | 디스플레이 (자동) | `data-ad-slot="0000000004"` |
| 5 | 꿈해몽 채팅 in-feed | 인피드 (fluid) | `data-ad-slot="0000000005"` |
| 6 | 오늘의 운세 하단 | 디스플레이 (자동) | `data-ad-slot="0000000006"` |

각 광고 단위 생성 후 표시되는 **슬롯 ID (10자리 숫자)** 를 메모장에 기록해두세요.

---

## Step 5. ads.txt 업로드 + 검증

`ads.txt` 는 이미 사이트 루트에 존재합니다 (`/ads.txt` URL 로 접근 가능).
Step 7 의 자동 교체 스크립트를 실행하면 PLACEHOLDER → 실제 publisher ID 로 변환됩니다.

검증:
```
https://cheonmyeongdang.vercel.app/ads.txt
```
브라우저에서 열어 다음 형식이 보여야 합니다:
```
google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0
```

AdSense 콘솔 → **사이트 → ads.txt 상태** 에서 **인증됨** 으로 표시되면 OK.

---

## Step 6. 정책 검토 대기

- 평균 검토 기간: **1~14일** (한국은 보통 3~7일)
- 거절 사유 1순위: 콘텐츠 부족 → 천명당은 9000+ 라인 콘텐츠로 충분
- 거절 사유 2순위: privacy.html / terms.html 누락 → 이미 존재
- 거절 사유 3순위: 사이트 navigation 미흡 → 천명당은 9개 메뉴 보유
- 거절 사유 4순위: ads.txt 미설정 → Step 5 완료 시 해결

검토 결과는 가입 시 사용한 Gmail 로 통보됩니다.

---

## Step 7. 승인 후 자동 코드 교체

승인 메일을 받으면 다음 명령 1줄로 모든 PLACEHOLDER 가 교체됩니다.

```bash
cd C:/Users/hdh02/Desktop/cheonmyeongdang
python scripts/adsense_apply.py
```

대화형으로 다음 정보를 입력합니다:
- Publisher ID: `1234567890123456` (ca-pub- 뒤 16자리)
- 슬롯 #1~6: 각 10자리 숫자

또는 인자 직접 전달:
```bash
python scripts/adsense_apply.py \
    --pub 1234567890123456 \
    --slot1 1111111111 --slot2 2222222222 --slot3 3333333333 \
    --slot4 4444444444 --slot5 5555555555 --slot6 6666666666
```

스크립트가 처리하는 것:
1. `index.html` 의 ca-pub-PLACEHOLDER 6곳 자동 교체
2. `index.html` 의 data-ad-slot 6개 자동 교체
3. `ads.txt` 의 pub-PLACEHOLDER 자동 교체
4. `.bak` 백업 파일 생성

이후 Vercel 배포:
```bash
git add index.html ads.txt
git commit -m "AdSense: ca-pub + 6개 slot ID 적용"
git push
```
Vercel 이 자동 빌드/배포 (보통 60초 이내).

---

## 천명당 콘텐츠 정책 위험 점검

| 카테고리 | 천명당 적용 여부 | 대응 방안 |
|---------|--------------|---------|
| 도박/사행성 (로또 번호 추천) | 다른 Agent 추가 진행 중 | 페이지 하단 면책 문구 명시: "재미용이며 당첨 보장 X" |
| 미성년자 노출 | 자동 차단 X (자발적 방문) | privacy.html 에 14세 이상 명시 |
| 의료/건강 (관상에 건강 분석 포함) | 일반적 안내 수준 | "의학적 진단 아님" 면책 명시 |
| 점술 콘텐츠 (사주/관상/타로/꿈해몽) | OK — Google 정책상 일반 허용 | 별도 조치 없음 |
| 폭력/혐오 | 없음 | 해당 없음 |

### 권장 면책 문구 위치
- privacy.html 하단
- 사주/관상/타로 결과 페이지 하단 (작은 글씨)

권장 문구 예시:
```
※ 천명당의 모든 운세 콘텐츠는 전통 명리학 기반의 재미용 서비스입니다.
   의학적·법적 진단이나 미래 보장 효력이 없으며,
   본 서비스를 이용한 의사결정의 결과는 이용자 본인에게 있습니다.
```

---

## 트러블슈팅

### "value not in valid format" 에러
→ ca-pub ID 가 16자리 숫자가 아닌 경우. 앞의 `ca-pub-` 제외하고 16자리 숫자만 입력.

### ads.txt "인증되지 않음" 상태
→ `/ads.txt` 가 200 으로 응답하는지 확인. Vercel은 정적 파일 자동 서빙.
→ ca-pub 값이 정확한지 확인 (Publisher ID 와 일치해야 함).

### 광고가 안 보임 (코드 적용 후)
- AdSense 승인 직후 24시간 광고 게재 안 될 수 있음 (정상)
- 광고 차단기 (uBlock, AdBlock) 비활성 후 확인
- 콘솔에서 `adsbygoogle.push() error: No slot size for availableWidth=0` → 광고 슬롯 컨테이너 width 가 0 인 케이스. 부모 div 의 width 확인.

### 거절 후 재신청
- 거절 메일 사유 확인 → 보완 → AdSense 콘솔에서 **검토 요청** 클릭
- 같은 Gmail 로 재신청 가능 (제한 없음)

---

## 예상 수익 (참고용 시뮬레이션)

| 일 방문자 | 예상 클릭률 | 예상 CPM | 월 예상 수익 |
|----------|----------|---------|----------|
| 100명     | 0.5~1%   | $0.5~2   | $1.5~6     |
| 1,000명   | 0.5~1%   | $0.5~2   | $15~60     |
| 10,000명  | 0.5~1%   | $0.5~2   | $150~600   |

> 한국어 운세 카테고리는 일반적으로 CPM $0.5~1.5 (영어 IT/금융 카테고리 대비 낮음).
> 광고 게재 위치 최적화로 +30~50% 개선 가능.

---

## 다음 단계 (승인 후)

1. **Search Console 연동** → 검색 유입 데이터 + AdSense 매칭
2. **Auto ads** 활성화 검토 → 페이지 자동 광고 추가 (수동 6슬롯 + 보완)
3. **AdSense 실험** → 광고 형식 A/B 테스트
4. **세금 정보** → 한국 사업자 자동 원천징수 처리

---

문서 작성: 2026-04-27 / 사이트: cheonmyeongdang.vercel.app
스크립트: `scripts/adsense_precheck.py` , `scripts/adsense_apply.py`
