-- 천명당 Supabase events 부트스트랩
-- 데이터 부서 (#12) — GA4 보완용 서버사이드 이벤트 적재 + 퍼널/매출 뷰
-- 적용: Supabase 프로젝트 생성 후 SQL Editor에 그대로 붙여넣기 (한 번만 실행)
--
-- 사용 흐름:
--   api/*.js  →  service_role 키로 events INSERT
--   대시보드 →  events_daily / payment_funnel / sku_revenue_30d view 조회
-- 커스텀 이벤트 예: page_view / cta_click / pay_attempt / pay_success / pay_fail / refund
-- 모든 PII는 events.props 안에 키 단위로만(생년월일·이메일은 절대 INSERT 금지)

-- ─────────────────────────── extensions ───────────────────────────
create extension if not exists "pgcrypto";

-- ─────────────────────────── core table ───────────────────────────
create table if not exists public.events (
  id           uuid primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  event_name   text        not null check (char_length(event_name) <= 64),
  session_id   text,
  user_id      text,
  page_path    text,
  ref_url      text,
  utm_source   text,
  utm_medium   text,
  utm_campaign text,
  device       text check (device in ('mobile','tablet','desktop','unknown')) default 'unknown',
  country      text,
  sku          text,
  amount_krw   integer,
  ip_hash      text,           -- IP는 sha256 해시만 적재 (PII 회피)
  ua           text,
  props        jsonb           not null default '{}'::jsonb
);

create index if not exists events_created_at_idx on public.events (created_at desc);
create index if not exists events_event_name_idx on public.events (event_name);
create index if not exists events_session_idx    on public.events (session_id);
create index if not exists events_sku_idx        on public.events (sku) where sku is not null;
create index if not exists events_props_gin_idx  on public.events using gin (props);

comment on table public.events is '천명당 통합 이벤트 로그 (GA4 보완 — 매출/환불/퍼널 SoT)';

-- ─────────────────────────── RLS ───────────────────────────
alter table public.events enable row level security;

drop policy if exists "events_service_insert" on public.events;
drop policy if exists "events_service_read"   on public.events;
drop policy if exists "events_no_anon_read"   on public.events;

-- service_role만 insert/read. anon/authenticated 모두 차단.
create policy "events_service_insert" on public.events
  for insert to service_role with check (true);

create policy "events_service_read" on public.events
  for select to service_role using (true);

-- ─────────────────────────── helper RPC ───────────────────────────
-- api/*.js에서 호출할 단일 RPC. 클라이언트 키로는 호출 불가 (security definer + service_role 추천).
create or replace function public.log_event(
  p_event_name text,
  p_props      jsonb default '{}'::jsonb,
  p_session_id text default null,
  p_user_id    text default null,
  p_page_path  text default null,
  p_ref_url    text default null,
  p_sku        text default null,
  p_amount_krw integer default null
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  new_id uuid;
begin
  insert into public.events (
    event_name, props, session_id, user_id,
    page_path, ref_url, sku, amount_krw,
    utm_source, utm_medium, utm_campaign, country, device, ip_hash, ua
  ) values (
    p_event_name,
    coalesce(p_props, '{}'::jsonb),
    p_session_id,
    p_user_id,
    p_page_path,
    p_ref_url,
    p_sku,
    p_amount_krw,
    nullif(p_props->>'utm_source',''),
    nullif(p_props->>'utm_medium',''),
    nullif(p_props->>'utm_campaign',''),
    nullif(p_props->>'country',''),
    coalesce(nullif(p_props->>'device',''), 'unknown'),
    nullif(p_props->>'ip_hash',''),
    nullif(p_props->>'ua','')
  )
  returning id into new_id;
  return new_id;
end;
$$;

revoke all on function public.log_event(text, jsonb, text, text, text, text, text, integer) from public, anon, authenticated;
grant execute on function public.log_event(text, jsonb, text, text, text, text, text, integer) to service_role;

-- ─────────────────────────── analytics views ───────────────────────────
-- 일별 PV/UU
create or replace view public.events_daily as
select
  date_trunc('day', created_at)::date         as day,
  count(*)                                    as total_events,
  count(*) filter (where event_name = 'page_view') as page_views,
  count(distinct session_id)                  as sessions,
  count(distinct user_id)                     as users
from public.events
where created_at >= now() - interval '90 days'
group by 1
order by 1 desc;

-- 결제 퍼널 (방문 → CTA → 시도 → 성공)
create or replace view public.payment_funnel as
with f as (
  select
    date_trunc('day', created_at)::date as day,
    count(*) filter (where event_name = 'page_view')   as visits,
    count(*) filter (where event_name = 'cta_click')   as cta_clicks,
    count(*) filter (where event_name = 'pay_attempt') as pay_attempts,
    count(*) filter (where event_name = 'pay_success') as pay_success,
    count(*) filter (where event_name = 'refund')      as refunds
  from public.events
  where created_at >= now() - interval '30 days'
  group by 1
)
select
  day, visits, cta_clicks, pay_attempts, pay_success, refunds,
  case when visits      > 0 then round(100.0 * cta_clicks   / visits,      2) end as ctr_pct,
  case when cta_clicks  > 0 then round(100.0 * pay_attempts / cta_clicks,  2) end as attempt_rate_pct,
  case when pay_attempts> 0 then round(100.0 * pay_success  / pay_attempts,2) end as success_rate_pct,
  case when visits      > 0 then round(100.0 * pay_success  / visits,      4) end as overall_conv_pct
from f
order by day desc;

-- SKU별 매출 (지난 30일)
create or replace view public.sku_revenue_30d as
select
  coalesce(sku, '(unknown)')           as sku,
  count(*) filter (where event_name = 'pay_success') as orders,
  coalesce(sum(amount_krw) filter (where event_name = 'pay_success'), 0) as revenue_krw,
  count(*) filter (where event_name = 'refund')      as refund_count,
  coalesce(sum(amount_krw) filter (where event_name = 'refund'), 0)      as refund_krw
from public.events
where created_at >= now() - interval '30 days'
group by sku
order by revenue_krw desc;

-- ─────────────────────────── retention (7d) ───────────────────────────
create or replace view public.retention_7d as
with first_seen as (
  select user_id, min(created_at)::date as cohort_day
  from public.events
  where user_id is not null
  group by user_id
),
returns as (
  select fs.cohort_day, e.user_id,
         (e.created_at::date - fs.cohort_day) as day_n
  from first_seen fs
  join public.events e on e.user_id = fs.user_id
  where e.created_at::date between fs.cohort_day and fs.cohort_day + 7
)
select cohort_day,
       count(distinct user_id) filter (where day_n = 0) as d0,
       count(distinct user_id) filter (where day_n = 1) as d1,
       count(distinct user_id) filter (where day_n = 3) as d3,
       count(distinct user_id) filter (where day_n = 7) as d7
from returns
where cohort_day >= current_date - interval '30 days'
group by cohort_day
order by cohort_day desc;

-- ─────────────────────────── 90일 이전 자동 파기 ───────────────────────────
-- pg_cron이 활성화돼 있으면 매일 03:00에 90일 초과 이벤트 삭제 (개인정보 보유기간 준수)
do $$
begin
  if exists (select 1 from pg_extension where extname = 'pg_cron') then
    perform cron.schedule(
      'events_purge_90d',
      '0 3 * * *',
      $cron$ delete from public.events where created_at < now() - interval '90 days'; $cron$
    );
  end if;
end $$;
