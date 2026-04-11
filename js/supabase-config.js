/**
 * ============================================================================
 * 천명당 Supabase 설정 파일
 * ============================================================================
 *
 * 🛠 설정 단계:
 *
 *   1) https://supabase.com 에서 무료 계정 생성
 *   2) New Project → 이름/비밀번호/리전(ap-northeast-2 서울 권장) 선택 → Create
 *   3) 프로젝트 생성 완료까지 약 1분 대기
 *   4) 좌측 메뉴 → Project Settings → API 진입, 다음 두 값 복사:
 *         • Project URL        (e.g. https://abcdefghijk.supabase.co)
 *         • anon public key    (eyJhbGciOi... 로 시작하는 긴 JWT)
 *   5) 이 파일의 url, anonKey 에 붙여넣기
 *   6) SQL Editor → New query → supabase/schema.sql 전체 복붙 → Run
 *   7) Authentication → Users → Invite user → 관리자 이메일 등록
 *      → 이메일 수신 링크로 비밀번호 설정 (admin.html 로그인용)
 *   8) 아래 enabled 값을 true 로 변경
 *   9) 배포 후 index.html 의 불만 폼에서 테스트 제출
 *  10) admin.html 진입 → 로그인 → 접수 데이터 확인
 *
 * 🔐 보안 참고:
 *   - anon key 는 공개해도 안전합니다 (브라우저에 노출되는 것이 정상).
 *     RLS 정책이 실제 접근 통제를 담당합니다.
 *   - service_role key 는 절대 이 파일에 넣지 마세요 (서버 전용).
 *
 * ⚠️ enabled: false 인 동안에는 불만이 localStorage 에만 저장됩니다.
 *    설정을 완료한 뒤에 true 로 바꿔야 Supabase 로 전송됩니다.
 * ============================================================================
 */
window.SUPABASE_CONFIG = {
  url: 'YOUR_SUPABASE_PROJECT_URL',
  anonKey: 'YOUR_SUPABASE_ANON_KEY',
  enabled: false
};
