-- ============================================================================
-- 천명당 Supabase 스키마 (Complaints + RLS policies)
-- ============================================================================
--
-- 📋 적용 방법:
--   1) https://supabase.com/dashboard 에서 프로젝트 선택
--   2) 좌측 메뉴 → SQL Editor → New query
--   3) 이 파일 전체를 복사해서 붙여넣기
--   4) 우측 상단 [Run] 버튼 클릭
--   5) 에러 없이 "Success. No rows returned" 나오면 완료
--
-- 🔐 RLS 정책 요약:
--   - INSERT: anon(비로그인 사용자 포함) 모두 가능 → 폼 제출 허용
--   - SELECT/UPDATE/DELETE: authenticated 유저만 → 관리자 대시보드용
--
-- 🙋 관리자 초대 (대시보드에서 별도 수행):
--   Supabase Dashboard → Authentication → Users → [Invite user]
--   → 이메일 입력 → 이메일 수신 링크 클릭 → 비밀번호 설정 완료
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1) 테이블 생성
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.complaints (
  id            text PRIMARY KEY,
  name          text,
  tel           text,
  email         text,
  type          text,
  detail        text NOT NULL CHECK (length(detail) >= 10 AND length(detail) <= 5000),
  rating        int  DEFAULT 0 CHECK (rating BETWEEN 0 AND 5),
  analysis      jsonb,
  submitted_at  timestamptz NOT NULL DEFAULT now(),
  created_at    timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.complaints IS '천명당 고객지원 부서 불만 접수 기록';


-- ----------------------------------------------------------------------------
-- 2) 인덱스
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS complaints_submitted_at_idx
  ON public.complaints (submitted_at DESC);

CREATE INDEX IF NOT EXISTS complaints_category_idx
  ON public.complaints ((analysis->'category'->>'key'));

CREATE INDEX IF NOT EXISTS complaints_severity_idx
  ON public.complaints (((analysis->>'severity')::int) DESC);


-- ----------------------------------------------------------------------------
-- 3) RLS 활성화
-- ----------------------------------------------------------------------------
ALTER TABLE public.complaints ENABLE ROW LEVEL SECURITY;


-- ----------------------------------------------------------------------------
-- 4) 정책: 누구나 불만 접수 (INSERT)
-- ----------------------------------------------------------------------------
DROP POLICY IF EXISTS "anyone can submit complaint" ON public.complaints;
CREATE POLICY "anyone can submit complaint"
  ON public.complaints
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (
    -- 기본 유효성 (서버 사이드 최소 가드)
    length(detail) >= 10
    AND length(detail) <= 5000
    AND rating BETWEEN 0 AND 5
  );


-- ----------------------------------------------------------------------------
-- 5) 정책: 관리자(로그인 유저)만 전체 조회
-- ----------------------------------------------------------------------------
DROP POLICY IF EXISTS "authenticated users can read" ON public.complaints;
CREATE POLICY "authenticated users can read"
  ON public.complaints
  FOR SELECT
  TO authenticated
  USING (true);


-- ----------------------------------------------------------------------------
-- 6) 정책: 관리자만 분석 결과 업데이트 (재판독용)
-- ----------------------------------------------------------------------------
DROP POLICY IF EXISTS "authenticated users can update" ON public.complaints;
CREATE POLICY "authenticated users can update"
  ON public.complaints
  FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);


-- ----------------------------------------------------------------------------
-- 7) 정책: 관리자만 삭제
-- ----------------------------------------------------------------------------
DROP POLICY IF EXISTS "authenticated users can delete" ON public.complaints;
CREATE POLICY "authenticated users can delete"
  ON public.complaints
  FOR DELETE
  TO authenticated
  USING (true);


-- ----------------------------------------------------------------------------
-- 8) 권한 grant (Supabase 기본과 일치하지만 명시)
-- ----------------------------------------------------------------------------
GRANT INSERT ON public.complaints TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.complaints TO authenticated;


-- ============================================================================
-- 설치 완료 확인 쿼리 (선택):
--   SELECT policyname, cmd, roles FROM pg_policies WHERE tablename = 'complaints';
-- ============================================================================
