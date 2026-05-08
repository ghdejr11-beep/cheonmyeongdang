# Play Console AAB 업로드 1클릭 가이드 (요약)

> **시급도**: 🔥 매출 직결 (천명당 v1.3.1 → 매직링크 OTP + 4언어 + 인플루언서 쿠폰)
> **사용자 시간**: ~5분
> **매출 임팩트**: 일 다운로드 10~30 → 정기결제 ₩2,900/mo × 5~10 신규 = ₩14,500~₩29,000/mo
> **마지막 업데이트**: 2026-05-06

복붙 텍스트 ✂ 표시. **상세 가이드는 `docs/play_console_upload_guide.md` 참조**.

---

## 0. 사전 점검 (자동 완료)

- ✅ AAB 검증: `python scripts/check_aab_validity.py` → 통과
- ✅ AAB 위치: `android/app/build/outputs/bundle/release/app-release.aab` (11.73 MB)
- ✅ versionCode: 8 / versionName: 1.3.1
- ✅ 4언어 출시 노트 준비 완료 (ko/en/ja/zh — 본 가이드 Step 4)
- ✅ 매직링크 OTP / PDF 30p 종합운세 / AI Q&A 챗 / 시각화 차트 4종 통합
- ✅ 단계적 출시 20% 권장 (안정성 검증)

---

## 1. Play Console 진입 (30초)

**URL**: https://play.google.com/console

- Google 계정: `ghdejr11@gmail.com`
- 앱: **천명당** (앱 ID `4975834141794355754`)
- 좌측: `Release` → `Production`

⚠️ **알파/베타에 동일 AAB 존재시** → `Promote to Production` 1클릭 (새 업로드 불필요).

---

## 2. AAB 업로드 (2분)

1. `Create new release` 버튼
2. App bundles 섹션 → `Upload` 또는 드래그&드롭:

```
D:\cheonmyeongdang\android\app\build\outputs\bundle\release\app-release.aab
```

3. 업로드 완료 후 versionCode 8, versionName 1.3.1 표시 확인.

---

## 3. 출시 노트 4언어 paste (1분)

### 한국어 (ko-KR) ✂

```
v1.3.1 업데이트
- 인플루언서 쿠폰 시스템 출시
- 매직링크 OTP 로그인 (비밀번호 없음)
- AI Q&A 챗 (사주 자연어 질문)
- 종합운세 PDF 30페이지 다운로드
- 시각화 차트 4종 (오행/십신/대운/세운)
```

### English (en-US) ✂

```
v1.3.1 update
- New influencer coupon system
- Magic-link OTP login (no password)
- AI Q&A chat (Saju natural-language)
- 30-page yearly fortune PDF download
- 4 visualization charts (5 elements, 10 stars, 10-year, yearly)
```

### 日本語 (ja-JP) ✂

```
v1.3.1アップデート
- インフルエンサークーポンシステム導入
- マジックリンクOTPログイン（パスワード不要）
- AI質問チャット（四柱推命を自然言語で）
- 総合運勢PDF 30ページのダウンロード
- 可視化チャート4種（五行・十神・大運・歳運）
```

### 中文 (zh-CN) ✂

```
v1.3.1 更新
- 新增网红优惠券系统
- 魔法链接 OTP 登录（无需密码）
- AI 问答聊天（四柱八字自然语言）
- 30 页年度运势 PDF 下载
- 4 种可视化图表（五行/十神/大运/流年）
```

---

## 4. 단계적 출시 20% (1분)

1. `Rollout percentage` → **20%** 입력 (권장)
2. `Review release` 클릭
3. 변경 사항 검증 → `Start rollout to Production`

⚠️ **20% → 50% → 100%** 일주일에 걸쳐 자동 ramp (Play Console 자동 진행)
⚠️ ANR/크래시 0.47% 초과시 즉시 stop (Android vitals 알림)

---

## 5. 사용자만 가능한 액션 (3건)

1. Play Console 로그인 (Google 계정)
2. AAB 업로드 (드래그&드롭 1클릭)
3. `Start rollout` 버튼 (1클릭)

**총 ~5분**.

---

## 6. 완료 후 자동 후속

- 검토 통과 알림 (1~2일) → 사용자 푸시
- 크래시 모니터링 (Android vitals) → 임계값 초과시 자동 stop
- 정기결제 매출 추적 (`unified_revenue.py`)
- 3.5★ 이하 리뷰 즉시 응답 자동화

---

## 7. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `versionCode 8 already used` | 동일 versionCode 업로드 시도 | versionCode 9로 올리고 재빌드 (`gradlew.bat bundleRelease`) |
| `Signature does not match` | 키스토어 변경 | 기존 release.keystore 사용 (`D:\backup_keystores\` 확인) |
| 검토 거부 (개인정보) | 권한 미설명 | `/privacy.html` URL 등록 확인 |

---

## 자동 업로드 향후 셋업 (선택)

1회 셋업으로 다음 빌드부터 클로드가 자동 업로드 가능:

1. https://console.cloud.google.com → IAM → 서비스 계정 생성
2. Play Console → 설정 → API 액세스 → 서비스 계정 연결, **Release Manager** 권한
3. JSON 키 → `.secrets/play-service-account.json` 저장 (gitignore)
4. `pip install google-api-python-client google-auth`
5. 다음 빌드부터 `androidpublisher.edits` API로 자동 업로드

---

**상세 가이드**: `docs/play_console_upload_guide.md` (전체 161줄)
