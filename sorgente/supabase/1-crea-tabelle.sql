-- Gestione Lavori: archivio condiviso online
-- Incolla tutto nel SQL Editor di Supabase e premi "Run".
-- Si puo' rieseguire senza perdere dati.

create table if not exists public.voci (
  id         text primary key,
  tipo       text not null,            -- clienti | lavori | utenti | del
  dati       jsonb,
  mod        bigint not null default 0, -- ora dell'ultima modifica (ms)
  eliminato  boolean not null default false,
  aggiornato timestamptz not null default now()
);
create table if not exists public.impostazioni (chiave text primary key, valore text);

-- nessuno puo' leggere/scrivere le tabelle direttamente:
-- si passa solo dalle due funzioni qui sotto, che chiedono il codice del team
alter table public.voci enable row level security;
alter table public.impostazioni enable row level security;
revoke all on public.voci, public.impostazioni from anon, authenticated;

insert into public.impostazioni (chiave, valore) values ('codice', 'SCRIVI-QUI-IL-CODICE-DEL-TEAM')
on conflict (chiave) do update set valore = excluded.valore;

create or replace function public.lavori_leggi(codice text)
returns setof public.voci
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from impostazioni i where i.chiave = 'codice' and i.valore = codice) then
    raise exception 'codice errato';
  end if;
  return query select * from voci;
end $$;

create or replace function public.lavori_scrivi(codice text, righe jsonb)
returns integer
language plpgsql security definer set search_path = public as $$
declare n integer;
begin
  if not exists (select 1 from impostazioni i where i.chiave = 'codice' and i.valore = codice) then
    raise exception 'codice errato';
  end if;
  insert into voci (id, tipo, dati, mod, eliminato, aggiornato)
  select r->>'id', r->>'tipo', r->'dati', coalesce((r->>'mod')::bigint, 0),
         coalesce((r->>'eliminato')::boolean, false), now()
  from jsonb_array_elements(righe) r
  on conflict (id) do update
    set tipo = excluded.tipo, dati = excluded.dati, mod = excluded.mod,
        eliminato = excluded.eliminato, aggiornato = now()
    where voci.mod <= excluded.mod;      -- vince sempre la modifica piu' recente
  get diagnostics n = row_count;
  return n;
end $$;

revoke all on function public.lavori_leggi(text), public.lavori_scrivi(text, jsonb) from public;
grant execute on function public.lavori_leggi(text), public.lavori_scrivi(text, jsonb) to anon, authenticated;
