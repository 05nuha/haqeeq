-- Haqeeq schema (CONTRACT). Run in Supabase SQL editor or `supabase db push`.
-- All writes go through the service-role key on the server (bypasses RLS).
-- The dashboard uses the anon key: SELECT only on the safe tables below.

create table if not exists official_posts (
  id          text primary key,            -- slug, e.g. 'mohre_working_hours'
  title       text not null,               -- English title
  title_ar    text,                        -- Arabic title
  issuer      text not null,               -- e.g. 'Ministry of Human Resources & Emiratisation (MOHRE)'
  date        text,                        -- display date 'YYYY-MM-DD'
  phash       text not null,               -- 16 hex chars, engine.phash()
  image_path  text not null                -- storage path in bucket 'media', e.g. 'official/<id>.png'
);

-- Known fakes already identified by analysts. A forward that matches one gets verdict
-- 'unverified' (never "proven fake") but its `detail` joins that fake's trending group.
create table if not exists known_fakes (
  id          text primary key,
  title       text not null,
  detail      text not null,               -- MUST equal the demo_seed scenario detail string
  phash       text not null,
  image_path  text not null                -- 'fakes/<id>.png'
);

-- Server-only: full phone numbers. anon/authenticated get nothing.
create table if not exists senders (
  id          bigserial primary key,
  phone       text unique not null,        -- E.164 without 'whatsapp:' prefix
  created_at  timestamptz default now()
);

create table if not exists reports (
  id            bigserial primary key,
  ts            timestamptz not null default now(),
  sender_masked text,                      -- '+97150•••123'
  sender_id     bigint references senders(id) on delete set null,
  kind          text not null check (kind in ('image','text','link')),
  verdict       text not null check (verdict in ('genuine','altered','unverified','scam_risk')),
  matched_id    text references official_posts(id) on delete set null,
  distance      int,                       -- pHash Hamming distance /64
  changed_pct   real,                      -- % pixels changed vs matched official
  heat          jsonb,                     -- 16x16 array of 0..1 change fractions (altered/genuine images)
  emirate       text,                      -- one of the 7 emirates (+ 'Al Ain' allowed as a city label)
  area          text,                      -- optional Dubai community name (Dubai Pulse lookup)
  detail        text,                      -- grouping key for "trending" + human description (English)
  ai_reason     text,                      -- Gemini Arabic reason (text checks), null if rules used
  ai_used       boolean default false,
  image_path    text,                      -- storage path 'incoming/<uuid>.jpg'
  seeded        boolean not null default false   -- true for demo background data (honest labelling)
);
create index if not exists reports_ts_idx on reports (ts desc);
create index if not exists reports_detail_idx on reports (detail);

create table if not exists corrections (
  detail      text primary key,
  ts          timestamptz not null default now(),
  message     text not null,
  recipients  int not null default 0,      -- reports with this detail (people reached in principle)
  delivered   int not null default 0       -- real WhatsApp messages actually sent via Twilio
);

-- Open data: trusted government entities (Bayanat entity list + Dubai Pulse org register).
create table if not exists entities (
  id       bigserial primary key,
  name     text not null,
  name_ar  text,
  kind     text,                           -- 'federal_entity' | 'dubai_entity' | ...
  domain   text,                           -- official web domain if known
  source   text not null                   -- dataset name, e.g. 'Bayanat — Entities'
);

-- Open data: population per emirate (FCSC / Bayanat) for per-100k normalisation.
create table if not exists population (
  emirate       text primary key,
  population    int not null,
  older_share   real,                      -- share aged 60+ if available, else null
  year          int,
  source        text not null
);

-- Open data: Dubai communities (Dubai Pulse area lookup + population by community).
create table if not exists dubai_areas (
  code        text primary key,
  name_en     text,
  name_ar     text,
  population  int,
  source      text not null
);

-- Catalogue shown in the dashboard "Open data" panel (copied from DATA_SOURCES.md).
create table if not exists open_datasets (
  id         text primary key,
  name       text not null,
  publisher  text not null,
  portal     text not null,                -- 'Bayanat' | 'Dubai Pulse' | 'FCSC Open Data'
  url        text not null,
  accessed   date,
  powers     text not null,                -- which feature uses it
  rows       int
);

-- ---------- RLS ----------
alter table official_posts enable row level security;
alter table known_fakes    enable row level security;
alter table senders        enable row level security;
alter table reports        enable row level security;
alter table corrections    enable row level security;
alter table entities       enable row level security;
alter table population     enable row level security;
alter table dubai_areas    enable row level security;
alter table open_datasets  enable row level security;

-- senders: NO policies => deny-all for anon/authenticated. Also revoke grants.
revoke all on senders from anon, authenticated;

-- reports: anon may read every column EXCEPT sender_id (column-level grant).
revoke all on reports from anon, authenticated;
grant select (id, ts, sender_masked, kind, verdict, matched_id, distance, changed_pct, heat,
              emirate, area, detail, ai_reason, ai_used, image_path, seeded)
  on reports to anon, authenticated;

do $$ begin
  create policy "public read official_posts" on official_posts for select to anon, authenticated using (true);
  create policy "public read known_fakes"    on known_fakes    for select to anon, authenticated using (true);
  create policy "public read reports"        on reports        for select to anon, authenticated using (true);
  create policy "public read corrections"    on corrections    for select to anon, authenticated using (true);
  create policy "public read entities"       on entities       for select to anon, authenticated using (true);
  create policy "public read population"     on population     for select to anon, authenticated using (true);
  create policy "public read dubai_areas"    on dubai_areas    for select to anon, authenticated using (true);
  create policy "public read open_datasets"  on open_datasets  for select to anon, authenticated using (true);
exception when duplicate_object then null; end $$;

-- ---------- Realtime ----------
do $$ begin
  alter publication supabase_realtime add table reports;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table corrections;
exception when duplicate_object then null; end $$;

-- ---------- Storage ----------
-- Bucket 'media' is public-read; object names under incoming/ are random UUIDs.
-- Writes only with the service-role key (no insert/update policies for anon).
insert into storage.buckets (id, name, public) values ('media', 'media', true)
  on conflict (id) do nothing;
