-- Applied to the Supabase project bivccpsnzzolxuqdvhfu on 13 October 2026.
-- Caps on offtheroll_track(), so that a script calling the public function in
-- a loop cannot fill the table or the database. Real use before this was at
-- most 259 calls and 42 rows a day.
--   A day takes at most 3,000 distinct (kind, item) rows. Past that, calls
--   for an item not already counted that day are dropped.
--   A day takes at most 500,000 counts in all. Past that, every call is
--   dropped.
-- A dropped call returns normally, with nothing to tell a caller it was
-- dropped. The checks read only today's rows, through the primary key.
create or replace function public.offtheroll_track(p_kind text, p_item text)
returns void
language plpgsql
security definer
set search_path to 'public'
as $$
declare
  v_item text := coalesce(nullif(p_item, ''), '/');
  v_rows integer;
  v_total bigint;
begin
  if p_kind not in ('view','share','download','install','search') then
    raise exception 'invalid kind';
  end if;
  if length(p_item) > 120 or p_item !~ '^[a-zA-Z0-9/_.#-]*$' then
    raise exception 'invalid item';
  end if;
  select count(*), coalesce(sum(count), 0) into v_rows, v_total
    from offtheroll_metrics where day = current_date;
  if v_total >= 500000 then
    return;
  end if;
  if v_rows >= 3000 and not exists (
    select 1 from offtheroll_metrics
     where day = current_date and kind = p_kind and item = v_item) then
    return;
  end if;
  insert into offtheroll_metrics(kind, item, count) values (p_kind, v_item, 1)
  on conflict (day, kind, item) do update set count = offtheroll_metrics.count + 1;
end $$;
revoke all on function public.offtheroll_track(text, text) from public;
grant execute on function public.offtheroll_track(text, text) to anon;
