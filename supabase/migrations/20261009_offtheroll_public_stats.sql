-- Applied to the Supabase project bivccpsnzzolxuqdvhfu on 9 October 2026.
-- offtheroll.in's totals for display on its front page: sums only, never a
-- page or a day. The table stays closed to the public key; this function is
-- the one thing it can read. Verified with the anon key: the function returns
-- the totals, a read of the table answers 401.
create or replace function public.offtheroll_public_stats()
returns json
language sql
security definer
set search_path to 'public'
as $$
  select json_build_object(
    'views',     coalesce((select sum(count) from offtheroll_metrics where kind = 'view'), 0),
    'shares',    coalesce((select sum(count) from offtheroll_metrics where kind = 'share'), 0),
    'downloads', coalesce((select sum(count) from offtheroll_metrics where kind = 'download'), 0),
    'searches',  coalesce((select sum(count) from offtheroll_metrics where kind = 'search'), 0),
    'since',     (select min(day) from offtheroll_metrics)
  );
$$;
revoke all on function public.offtheroll_public_stats() from public;
grant execute on function public.offtheroll_public_stats() to anon;
