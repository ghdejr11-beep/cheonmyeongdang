# RapidAPI Listing Text — 4 Languages (ko / en / ja / zh)

Paste each block directly into the RapidAPI provider dashboard for the matching
locale. RapidAPI supports Title / Description per language at the API level and
reads them on the regional hub.

API base URL: `https://cheonmyeongdang.vercel.app`
Endpoints: `/calculate`, `/qa`, `/compatibility`, `/monthly-fortune`

---

## EN — English (default, primary)

### Title
Korean Saju (Bazi) — 4 Pillars, Compatibility, AI Q&A

### Tagline (140 chars)
Authentic Korean Saju / Bazi reading API. 4 pillars, 5-element balance, two-person compatibility, monthly fortune, free-form AI Q&A.

### Long description
Authentic Korean Saju / Chinese Bazi (Four Pillars of Destiny) reading API in 4 endpoints.

POST `/calculate` returns the four pillars (year/month/day/hour stems and branches in Hangul + Hanja), a complete five-element (Wood/Fire/Earth/Metal/Water) distribution, day-stem personality summary, lucky color, and lucky cardinal direction — plus a Claude-generated 3-sentence English advice paragraph.

POST `/qa` lets your users ask any free-form question in {ko/en/ja/zh}; we ground the Claude answer on their own four-pillar chart so output is personalized, not generic horoscope text.

POST `/compatibility` returns a 0–100 score between two birth records using classical Korean Gunghap rules (1,000-year-old marriage screening method) — element generative/controlling balance, day-stem match, branch harmony, ten-gods match.

POST `/monthly-fortune` returns 12 month-by-month outlooks for any year 2024–2030, each with wealth/love/health/career bullets and a sentiment score.

Built on the production Saju engine that powers cheonmyeongdang.vercel.app and the Korean Cheonmyeongdang Android app: solar-to-lunar conversion, classical solar-term boundaries, 60-Ganji cycle, 10-year daeun calculation, 12 yunseong life stages. No random outputs — algorithmic core; AI only on the natural-language layer.

Perfect for astrology apps, dating apps, name-checking products, character-design tools, K-culture content sites and personality quiz platforms targeting Korean, Chinese, Japanese, Vietnamese and global Asian-culture audiences.

### Categories
- Astrology
- AI / Machine Learning
- Lifestyle / Korean culture

### Tags
saju, bazi, four-pillars, korean-astrology, chinese-astrology, fortune-telling, five-elements, wuxing, hangul, korean, claude-ai, personality, daily-fortune, gunghap, k-culture, monthly-fortune, compatibility

---

## KO — 한국어

### Title
한국 사주(四柱) API — 4기둥·궁합·월운·AI Q&A

### Tagline (140자)
정통 한국 사주/명리학 API. 4기둥(천간지지), 오행 균형, 두 사람 궁합, 12달 월운, 자유형 AI 질문응답까지 4 endpoint 한 번에.

### Long description
정통 한국 사주(四柱)·명리학 추산 API. 4 endpoint 구성:

POST `/calculate` — 양력 생년월일시·성별 입력 시 4기둥(년·월·일·시) 천간지지(한글+한자), 오행(목·화·토·금·수) 분포, 일간 성격 요약, 행운 색·방위, Claude AI가 생성한 3문장 한국어 조언 paragraph 반환. 응답 3초 이내.

POST `/qa` — 사용자가 ko/en/ja/zh 어떤 언어로든 자유형 질문 입력. 본인 4기둥 명식에 grounding된 답변 3~5문장. 일반 운세 글이 아닌 본인 명식 기반 개인화 답변.

POST `/compatibility` — 두 사람 생년월일시 입력, 0~100점 궁합 점수. 천간 합·지지 합/충/형/파, 십신 매칭, 오행 상생상극 균형 분해 + 2문장 조언. 1,000년 한국 궁합법 기반.

POST `/monthly-fortune` — 본인 사주 + 임의 연도(2024~2030) 입력 시 12개월 운세 array 반환. 각 월별 재물/애정/건강/직장 + 감정 점수.

천명당(cheonmyeongdang.vercel.app) 안드로이드 앱과 동일 production 엔진: 양력→음력 변환, 정통 절기 경계, 60갑자, 10년 대운, 12운성. 랜덤 출력 X — 알고리즘 코어 + AI는 자연어 layer 한정.

타겟: 점성·운세·소개팅 앱, 작명 서비스, 캐릭터 설정 도구, K-컬처 콘텐츠, MBTI 대체 성격 테스트 — 한국·중국·일본·베트남·글로벌 아시아권.

### Categories
- 점성술
- AI / 머신러닝
- 라이프스타일 / 한국 문화

### Tags
사주, 명리학, 사주팔자, 한국점성술, 궁합, 월운, 오행, 천간지지, 갑자, 운세, 사주api, AI사주, 천명당

---

## JA — 日本語

### Title
韓国サジュ(四柱推命)API — 4柱・相性・月運・AI Q&A

### Tagline (140字)
本格派の韓国サジュ/四柱推命API。4柱(干支)、五行バランス、2人の相性、12ヶ月月運、自由質問AI回答を1つのAPIで提供。

### Long description
本場韓国サジュ(四柱推命)推命API。4 endpoint構成:

POST `/calculate` — 西暦生年月日時・性別を入力すると、年・月・日・時の四柱(天干地支のハングル+漢字)、五行(木火土金水)バランス、日干性格、ラッキーカラー・方位、Claude AIによる3文の日本語アドバイスを返却。応答3秒以内。

POST `/qa` — ユーザーがko/en/ja/zhいずれかの言語で自由質問を入力すると、本人の四柱命式にgroundingされた3〜5文の回答を返却。汎用占い文ではなく、本人命式に基づく個別化回答。

POST `/compatibility` — 2人の生年月日時を入力すると、0〜100点の相性スコア。天干合・地支合/沖/刑/破、十神マッチング、五行相生相克バランスの分解+2文アドバイス。1000年韓国の合婚術ベース。

POST `/monthly-fortune` — 本人サジュ+任意年(2024〜2030)を入力すると、12ヶ月分の月運をarrayで返却。各月の財運/恋愛運/健康運/仕事運+感情スコア。

天命堂(cheonmyeongdang.vercel.app)韓国Androidアプリと同じproductionエンジン:太陽暦→旧暦変換、正統節気境界、60干支、10年大運、12運星。ランダム出力なし — アルゴリズムコア+AIは自然言語層のみ。

ターゲット:占星・占い・マッチングアプリ、姓名判断、キャラ設定ツール、Kカルチャーコンテンツ、MBTI代替性格テスト — 韓国・中国・日本・ベトナム・グローバルアジア圏。

### Categories
- 占星術
- AI / 機械学習
- ライフスタイル / 韓国文化

### Tags
サジュ, 四柱推命, 韓国占い, 命式, 相性占い, 月運, 五行, 干支, 占いAPI, K占い, 天命堂, 合婚, 八字

---

## ZH — 繁體中文

### Title
韓國薩柱(四柱八字)API — 4柱・合婚・流月・AI問答

### Tagline (140字)
正統韓國薩柱/八字命理API。4柱(天干地支)、五行旺衰、雙人合婚、12月流月、自由問答AI回答,一個API一次到位。

### Long description
正統韓國薩柱(四柱八字)命理API。4 endpoint結構:

POST `/calculate` — 輸入陽曆生辰八字與性別,回傳年・月・日・時四柱(天干地支韓文+漢字)、五行(木火土金水)分布、日干性格、幸運色・方位,以及Claude AI生成的3句中文建議段落。回應3秒內。

POST `/qa` — 用戶以ko/en/ja/zh任一語言提自由問題,系統以本人四柱命盤為grounding,回傳3〜5句回答。非通用運勢文,而是基於本人命盤的個人化回應。

POST `/compatibility` — 輸入兩人生辰八字,回傳0〜100分合婚分數。天干合・地支合/沖/刑/破、十神配對、五行相生相剋平衡的細項分解+2句建議。1000年韓國合婚術為基礎。

POST `/monthly-fortune` — 輸入本人薩柱+任一年份(2024〜2030),回傳12個月流月array。每月財運/桃花/健康/事業+情緒分數。

天命堂(cheonmyeongdang.vercel.app)韓國Android App相同production引擎:陽曆→農曆轉換、正統節氣界線、60甲子、10年大運、12運星。無隨機輸出 — 演算法核心,AI僅用於自然語言層。

目標客群:占卜・占星・約會App、姓名學服務、角色設定工具、K文化內容、MBTI替代性格測驗 — 韓國・中國・日本・越南・全球亞洲圈。

### Categories
- 占星術
- AI / 機器學習
- 生活風格 / 韓國文化

### Tags
薩柱, 四柱八字, 韓國八字, 命盤, 合婚, 流月運勢, 五行, 天干地支, 算命API, K命理, 天命堂, 八字命理

---

## Pricing tiers (universal, language-agnostic)

| Tier   | Price       | Quota           | Overage     | Notes                                  |
|--------|-------------|-----------------|-------------|-----------------------------------------|
| FREE   | $0/mo       | 100 req / day   | hard cap    | Discovery; share-on-social welcome      |
| PRO    | $9.99/mo    | 5,000 req/day   | $0.002/req  | Indie devs, small apps (~150K/mo)       |
| ULTRA  | $49/mo      | 50,000 req/day  | $0.0008/req | Production apps, dating/quiz platforms  |
| MEGA   | $199/mo     | 1,000,000 req/mo| $0.0004/req | High-traffic content sites              |

Provider take (RapidAPI default 75%):
- PRO: $7.49/mo per subscriber
- ULTRA: $36.75/mo per subscriber
- 100 PRO subscribers = $749/mo passive

## Endpoint cheat-sheet (paste under each lang)

| Endpoint | Method | Use case |
|---|---|---|
| `/calculate` | POST | One-shot 4-pillar Saju reading + AI advice |
| `/qa` | POST | Free-form chat-style astrology Q&A |
| `/compatibility` | POST | Two-person Gunghap score 0–100 |
| `/monthly-fortune` | POST | 12-month forecast for any year 2024–2030 |

## Image / cover assets

- Logo: `/icons/saju-logo-512.png` (use existing `app_icon_512.png`)
- Cover: `/assets/feature_graphic_1024x500.png` (already in repo)
