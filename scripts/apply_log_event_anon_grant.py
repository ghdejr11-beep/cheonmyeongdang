"""log_event RPC 안전화 + anon grant 적용 (1회 실행).

Vercel Hobby 12-function 한도로 log-event 프록시 endpoint 추가 불가 →
대신 Supabase RPC 자체에 화이트리스트/크기 제한을 두고 anon 직접 호출 허용.
"""
import psycopg2

CONN_HOSTS = [
    "aws-0-ap-northeast-2",
    "aws-1-ap-northeast-2",
    "aws-0-ap-southeast-1",
    "aws-1-ap-southeast-1",
    "aws-0-ap-northeast-1",
    "aws-1-ap-northeast-1",
    "aws-0-us-east-1",
    "aws-1-us-east-1",
]
PWD = "nyS170GYA4Zs1tfe"
REF = "hznihnwqgiumxakshtse"
CONN = None  # will be discovered

SQL = r"""
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
  allowed text[] := array['page_view','cta_click','pay_attempt','pay_success','pay_fail','refund','subscribe','signup','modal_open','video_play'];
begin
  if not (p_event_name = any(allowed)) then return null; end if;
  if p_props is not null and pg_column_size(p_props) > 4096 then return null; end if;
  if char_length(coalesce(p_session_id,'')) > 80 then return null; end if;
  if char_length(coalesce(p_user_id,'')) > 80 then return null; end if;
  if char_length(coalesce(p_page_path,'')) > 256 then return null; end if;
  if char_length(coalesce(p_ref_url,'')) > 512 then return null; end if;
  if char_length(coalesce(p_sku,'')) > 64 then return null; end if;

  insert into public.events (
    event_name, props, session_id, user_id,
    page_path, ref_url, sku, amount_krw,
    utm_source, utm_medium, utm_campaign, country, device, ip_hash, ua
  ) values (
    p_event_name,
    coalesce(p_props, '{}'::jsonb),
    p_session_id, p_user_id, p_page_path, p_ref_url, p_sku, p_amount_krw,
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

grant execute on function public.log_event(text, jsonb, text, text, text, text, text, integer) to anon, authenticated;
"""

def main():
    last_err = None
    for host in CONN_HOSTS:
        for port in (6543, 5432):
            dsn = f"postgresql://postgres.{REF}:{PWD}@{host}.pooler.supabase.com:{port}/postgres"
            try:
                with psycopg2.connect(dsn, connect_timeout=10) as conn:
                    with conn.cursor() as cur:
                        cur.execute(SQL)
                    conn.commit()
                print(f"OK OK via {host}:{port}")
                return
            except Exception as e:
                last_err = f"{host}:{port} → {type(e).__name__}: {str(e)[:80]}"
                print(f"  FAIL {last_err}")
    raise SystemExit(f"FAILED — last error: {last_err}")

if __name__ == "__main__":
    main()
