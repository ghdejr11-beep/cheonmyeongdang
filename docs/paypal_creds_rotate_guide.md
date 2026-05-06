# PayPal LIVE 자격증명 rotate 가이드 (보안 사고 대응)

**작성일**: 2026-05-06
**Severity**: LOW (가장 낮은 평가) — 자세한 사유는 하단 "노출 범위 분석" 참조
**대상**: 천명당 PayPal LIVE Application

---

## 사건 요약

`departments/sales-collection/paypal_daily_monitor.py` 파일이 처음 작성될 때 PayPal LIVE creds가 함수 default param으로 hardcoded 되어있었음. audit Agent O가 발견 후 즉시 `.secrets` 환경변수 로딩 방식으로 강제 교체하여 commit (`c758279`).

### 노출 범위 분석 (사실)

| 항목 | 결과 |
|---|---|
| Hardcoded creds가 git history에 commit 됐는가? | **❌ 아니오** (`git log -S` pickaxe 검색 + `git grep` 모든 ref 0 hit) |
| 첫 commit 시점에 hardcoded 상태였는가? | ❌ 아니오 (c758279 diff에서 이미 .secrets 로딩 방식이었음) |
| GitHub origin/main에 push 됐는가? | 해당 없음 (commit에 노출분 없음) |
| GitHub repo visibility | **PUBLIC** (`api.github.com` 응답 `"private": false`) |
| 결론 | **노출분이 git에 들어간 적 없음** — local 작업 디렉토리에서 audit가 사전 차단함 |

**Severity LOW 사유**: 노출이 local working tree에서만 발생, public repo에 commit/push 된 적 없음. 단, 노출된 secret 값은 audit Agent가 task 메시지에 평문으로 인용했으므로 **세션 로그/지시 메시지 캐시에는 남아있을 수 있음**. 따라서 rotate는 "필수가 아닌 권장" 등급.

---

## 사용자 즉시 액션 — PayPal Secret rotate (5분 소요)

비록 git에 들어가지 않았으나 안전을 위해 **PayPal LIVE secret를 rotate** 하는 것을 권장.

### 1단계: PayPal Developer Dashboard 접속

URL: https://developer.paypal.com/dashboard/applications/live

(한국 사용자 접속 OK, hdh0203@naver.com 로그인 가능)

### 2단계: 천명당 LIVE App 선택

App Name: `cheonmyeongdang` 또는 본인이 등록한 LIVE 앱 이름 클릭.

### 3단계: Client Secret 재발급

App 상세 페이지에서:

1. "Client Secret" 항목 옆 `Show` 버튼 클릭하여 현재 값 확인 (참고용)
2. 같은 라인의 `Generate new secret` 또는 `Regenerate Client Secret` 버튼 클릭
3. 확인 dialog → `Generate` 클릭
4. 새로 발급된 secret 복사 (이 화면을 떠나면 다시 못 봄)

**주의**: Client ID(`AYS...`)는 그대로 유지되며 변경되지 않음. **Client Secret 만 바뀜**.

### 4단계: .secrets 파일 업데이트

`C:\Users\hdh02\Desktop\cheonmyeongdang\.secrets` 파일을 메모장으로 열고:

```
PAYPAL_CLIENT_ID=<기존 그대로>
PAYPAL_CLIENT_SECRET=<3단계에서 복사한 새 값으로 덮어쓰기>
```

저장 후 닫기.

### 5단계: Vercel env 동기화

Vercel 배포 환경(production)의 `PAYPAL_CLIENT_SECRET` 도 갱신:

```powershell
cd C:\Users\hdh02\Desktop\cheonmyeongdang
vercel env rm PAYPAL_CLIENT_SECRET production --yes
echo "<새 secret>" | vercel env add PAYPAL_CLIENT_SECRET production
vercel deploy --prod
```

또는 Vercel 웹 대시보드 → Project Settings → Environment Variables → `PAYPAL_CLIENT_SECRET` 편집.

### 6단계: 옛 secret 즉시 무효화 확인

PayPal Dashboard에서 새 secret 발급되는 시점에 **이전 secret은 자동 즉시 무효화**됨 (별도 revoke 액션 불필요).

### 7단계: 모니터 정상 동작 검증

```powershell
cd C:\Users\hdh02\Desktop\cheonmyeongdang
python departments\sales-collection\paypal_daily_monitor.py
```

`[CHECKED] 2026-05-06 — total_tx=N value=...` 출력되면 OK.

---

## 추가 보안 강화

1. **`.secrets` 권한 검사**
   - Windows ACL: `BUILTIN\Users:(I)(M)` (수정 권한) — 본인 PC 단일 사용자라 OK
   - Unix 환경 배포 시에는 `chmod 600 .secrets` 필수

2. **`.gitignore` 검증 완료** — `.secrets` 정상 ignore 됨

3. **사전 차단 자동화** — `departments/security/credential_leak_watcher.py` 신규 추가
   - regex로 `AYS...`, `EPP...`, `sk-...` 등 pattern detect
   - pre-commit hook으로 등록 시 commit 자체를 막음

4. **pre-commit hook 설치 (권장)**

   ```powershell
   cd C:\Users\hdh02\Desktop\cheonmyeongdang
   copy departments\security\credential_leak_watcher.py .git\hooks\pre-commit
   ```

   이후 `git commit` 시 자동으로 staged diff 검사 → leak 감지 시 commit abort.

---

## 결론

- **Git history는 깨끗함** (모든 ref에서 노출분 0 hit)
- **public repo지만 노출분이 들어간 적 없으므로 외부 유출 가능성 매우 낮음**
- **Rotate는 권장 (선택)** — 5분 소요, 무중단 가능
- **leak watcher 가동으로 재발 방지**
