-- Applied to the Supabase project bivccpsnzzolxuqdvhfu (democracy-by-design,
-- ap-south-1, Mumbai) on 2 October 2026. offtheroll.in's anonymous daily
-- tallies, the same design as Democracy by Design's metrics and track(): the
-- table is closed to the public key, and the one way in is
-- offtheroll_track(), which only adds one to a (day, kind, page) count.
-- No IP address, device id, cookie or search words are stored.
-- Verified with the anon key: the function answers 204, a bad item 400, and
-- a read of the table 401.
create table if not exists public.offtheroll_metrics (
  day   date not null default current_date,
  kind  text not null,
  item  text not null,
  count integer not null default 0,
  primary key (day, kind, item)
);
alter table public.offtheroll_metrics enable row level security;
revoke all on public.offtheroll_metrics from anon, authenticated;
comment on table public.offtheroll_metrics is 'offtheroll.in anonymous daily tallies (view, share, download, install, search). Written only through offtheroll_track(); no personal data.';

create or replace function public.offtheroll_track(p_kind text, p_item text)
returns void
language plpgsql
security definer
set search_path to 'public'
as $$
begin
  if p_kind not in ('view','share','download','install','search') then
    raise exception 'invalid kind';
  end if;
  if length(p_item) > 120 or p_item !~ '^[a-zA-Z0-9/_.#-]*$' then
    raise exception 'invalid item';
  end if;
  insert into offtheroll_metrics(kind, item, count) values (p_kind, coalesce(nullif(p_item, ''), '/'), 1)
  on conflict (day, kind, item) do update set count = offtheroll_metrics.count + 1;
end $$;
revoke all on function public.offtheroll_track(text, text) from public;
grant execute on function public.offtheroll_track(text, text) to anon;

-- To read the counts, in the Supabase SQL editor (the public key cannot):
--   select day, kind, item, count from offtheroll_metrics order by day desc, count desc;
