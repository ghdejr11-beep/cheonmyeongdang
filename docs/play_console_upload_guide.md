# 천명당 Play Console AAB 업로드 가이드

> 본 가이드는 클로드가 자동 검증한 AAB를 사용자가 1클릭 업로드하기 위한 절차서다.
> 자동 업로드는 **불가** — Google Play Developer API 서비스 계정 키
> (`.secrets/play-service-account.json`)가 미설정. 사용자 직접 업로드가 가장 빠르다.

## 0. 사전 검증 (자동 완료)

```bash
python scripts/check_aab_validity.py
```

검증 결과 (2026-05-06 기준):

| 항목 | 값 |
|-----|---|
| AAB 경로 | `android/app/build/outputs/bundle/release/app-release.aab` |
| 크기 | 11.73 MB (12,301,968 bytes) |
| 빌드 시각 | 2026-04-23 22:57 |
| 패키지 | `com.cheonmyeongdang.app` |
| versionCode | 8 |
| versionName | 1.3.1 |
| 권한 수 | 9 (광고/네트워크/포그라운드 등 정상) |
| ZIP 무결성 | OK (538 entries) |

→ 즉시 업로드 가능.

## 1. Play Console 진입

1. https://play.google.com/console 접속 (Google 계정: `ghdejr11@gmail.com`)
2. 앱 목록에서 **천명당** (앱 ID `4975834141794355754`) 클릭

## 2. 출시 트랙 선택

좌측 메뉴 → **출시(Release) > 프로덕션(Production)** 클릭.

> 이미 알파/베타 트랙에 동일 AAB가 있다면 트랙에서 **프로덕션으로 승격(Promote release)** 만 클릭하면 됨 — 새 업로드 불필요.

승격이 아니라 새 업로드가 필요한 경우 → **새 출시 만들기(Create new release)** 버튼.

## 3. AAB 업로드

1. **App bundles** 섹션에서 **Upload** 클릭
2. 파일 선택 또는 드래그앤드롭:

```
C:\Users\hdh02\Desktop\cheonmyeongdang\android\app\build\outputs\bundle\release\app-release.aab
```

3. 업로드 완료 후 versionCode 8, versionName 1.3.1 표시 확인.

## 4. 출시 노트 입력 (4개 언어)

> 각 언어 공백 포함 200자 내외, 줄바꿈 5개 이내 권장.

### 한국어 (ko-KR)

```
v1.3.1 업데이트
- 인플루언서 쿠폰 시스템 출시
- 명리학 7카드 리딩 추가 (총운/직업/재물/사랑/건강/관계/조언)
- 시각화 차트 4종 (오행 균형/십신/대운/세운)
- AI Q&A 챗봇으로 사주 질문 즉시 답변
- 매직링크 OTP 인증 + 한·영·일·중 4개 언어 지원
```

### English (en-US)

```
v1.3.1 update
- Influencer coupon system launched
- 7-card Saju reading (general/career/wealth/love/health/relationship/advice)
- 4 visualization charts (5 elements/10 deities/major fortune/yearly luck)
- AI Q&A chatbot for instant Saju questions
- Magic-link OTP login + Korean/English/Japanese/Chinese support
```

### 日本語 (ja-JP)

```
v1.3.1アップデート
- インフルエンサークーポンシステム開始
- 命理学7カードリーディング追加(総運/仕事/金運/恋愛/健康/人間関係/助言)
- 可視化チャート4種(五行/十神/大運/年運)
- AI Q&Aチャットで四柱推命質問に即回答
- マジックリンクOTPログイン + 韓·英·日·中4言語対応
```

### 中文 (zh-CN)

```
v1.3.1 更新
- 网红优惠券系统上线
- 命理学7张牌解读(总运/事业/财运/爱情/健康/人际/建议)
- 4种可视化图表(五行平衡/十神/大运/流年)
- AI问答聊天机器人即时解答四柱八字疑问
- 魔法链接OTP登录 + 韩·英·日·中4语言支持
```

## 5. 출시 검토 및 게시

1. 우측 상단 **다음(Next)** → 요약 확인
2. **출시 검토 시작(Start rollout to Production)** 클릭
3. 100% 출시 또는 단계적 출시(staged rollout 20%) 선택
   - 1.3.1은 메이저 변경 다수 → **20% staged 권장** (7일 후 100%)

## 6. 검토 대기

| 단계 | 예상 시간 |
|-----|---------|
| Google Play 정책 검토 | 1~3 영업일 |
| 새 콘텐츠 검토 (스토어 등록 변경 시) | +1~2일 |
| 단계적 출시 시작 | 검토 통과 직후 |
| 100% 출시 도달 | 7일 후 (20% → 50% → 100%) |
| 첫 다운로드 발생 | 검토 통과 24h 이내 (기존 알림 구독자) |

## 7. 출시 후 확인

1. **통계(Statistics)**: 다운로드/활성 사용자
2. **Android vitals**: ANR/크래시율 (Threshold: 0.47% / 1.09%)
3. **수익화 → Play Billing**: 정기결제 ₩2,900/월 / ₩29,900/년 매출 추적
4. **사용자 피드백 → 리뷰**: 3.5★ 이하 리뷰 즉시 응답

## 8. 자동화 향후 계획

자동 업로드가 필요하면 1회 셋업:

1. https://console.cloud.google.com → IAM → 서비스 계정 생성
2. Play Console → 설정 → API 액세스 → 서비스 계정 연결, **Release Manager** 권한
3. JSON 키 다운로드 → `C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets\play-service-account.json` 저장 (gitignore)
4. `pip install google-api-python-client google-auth`
5. 다음 빌드부터 클로드가 직접 업로드 (`androidpublisher.edits` API)

## 9. 트러블슈팅

| 증상 | 원인 | 해결 |
|-----|-----|-----|
| `versionCode 8 already used` | 동일 versionCode 업로드 시도 | `android/app/build.gradle`에서 versionCode 9로 올리고 `gradlew.bat bundleRelease` 재빌드 |
| `Signature does not match` | 키스토어 변경 | 기존 release.keystore 그대로 사용 (D:\ 백업 위치 확인) |
| `Missing 64-bit code` | armeabi-v7a only | gradle에 arm64-v8a 포함 확인 |
| 검토 거부 | 권한 미설명 | 개인정보 처리방침 URL `/privacy.html` 등록 확인 |

## 10. 핵심 변경 사항 (v1.3.0 → 1.3.1)

**사용자 측면:**
- 4개 언어 지원 (ko/en/ja/zh)
- 매직링크 OTP 로그인 (비밀번호 없음)
- PDF 30페이지 종합운세 다운로드
- AI Q&A 챗 (사주 자연어 질문)
- 시각화 차트 4종 (오행/십신/대운/세운)

**어드민 측면:**
- 인플루언서 쿠폰 발급 시스템
- Play Billing 정기결제 매출 대시보드 통합
- 4개 언어 출시 노트 + 메타데이터

---

**작성**: 클로드 에이전트
**검증**: `python scripts/check_aab_validity.py` 통과
**대상 파일**: `android/app/build/outputs/bundle/release/app-release.aab` (11.73 MB)
