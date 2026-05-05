# Testimonial 자리표시 템플릿 (2026-05-05)

**원칙**: 거짓 testimonial 절대 X (memory `legal_safety_first`). 첫 5명 인터뷰 → 동의 받은 후만 게시.

## landing 자리표시 HTML (천명당 / KORLENS)

```html
<section class="testimonials" id="testimonials">
  <h2>실제 사용자 후기</h2>
  <p class="muted">※ 첫 5명 인증 사용자 후기를 받는 중. 인터뷰 응해주신 분께 추가 풀이 1회 무료 제공.</p>

  <!-- 인증 후기 받기 전: 가치 약속만 표시 -->
  <div class="testimonial-empty">
    <p>아직 게시된 후기가 없습니다. 천명당의 무료 풀이를 사용해보시고 후기 남겨주시면 다음 풀이 1회 무료입니다.</p>
    <a href="mailto:ghdejr11+testimonial@gmail.com?subject=천명당%20후기">후기 보내기 →</a>
  </div>

  <!-- 인증 후기 발생 시 채울 자리표시 -->
  <!--
  <div class="testimonial-card">
    <p class="quote">"실제 후기 텍스트 (사용자 동의 후 게시)"</p>
    <p class="author">— 이니셜.K, 30대, 2026-05-XX</p>
  </div>
  -->
</section>
```

## 인터뷰 질문 (이메일 1건)

1. 천명당의 어떤 점이 가장 마음에 들었나요?
2. 어떤 풀이가 가장 도움됐나요? (사주 / 종합 / 신년 / 무료)
3. 친구/가족에게 추천한다면 어떤 말로 소개할 건가요?
4. 한 가지 더 추가됐으면 하는 기능?
5. **게시 동의** (이니셜 + 연령대까지만 게시. 실명 X) — 예/아니오

## 첫 5명 모집 액션

- 천명당 success.html 결제 완료 페이지에 "후기 1줄 → 다음 풀이 무료" CTA 추가 (이미 cross-sell 자리 있음)
- D+3 후속 메일 (`project_cheonmyeongdang_followup_sequence.md`) 시퀀스에 후기 요청 1건 추가
- 응답 0이면 D+14에 한 번 더 reminder

## 게시 시 법적 체크리스트
- [ ] 실명 X (이니셜만)
- [ ] 사용자 명시 동의 받음 (이메일 회신 캡처)
- [ ] 의료/투자/도박 효과 주장 X (memory `legal_safety_first`)
- [ ] 환불/즉시효과 보증 표현 X
