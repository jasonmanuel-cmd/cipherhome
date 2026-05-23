-- ============================================================
-- CIPHER SOVEREIGN v2.0 — INITIAL SCHEMA
-- Run this in Supabase SQL Editor to create all required tables.
-- Project: expcinwdxxlfgkuxpirq
-- ============================================================

-- Enable UUID generation
create extension if not exists "pgcrypto";

-- ============================================================
-- MEMORY
-- ============================================================
create table if not exists cipher_memory_chunks (
  id            uuid primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  content       text not null,
  summary       text,
  category      text not null default 'decision',
  source        text default 'local',
  confidence_score float default 0.9,
  is_active     boolean not null default true
);
create index if not exists idx_memory_category   on cipher_memory_chunks (category);
create index if not exists idx_memory_active     on cipher_memory_chunks (is_active);
create index if not exists idx_memory_created    on cipher_memory_chunks (created_at desc);

-- ============================================================
-- FLAGS
-- ============================================================
create table if not exists cipher_active_flags (
  id            uuid primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  title         text not null,
  issue         text not null,
  flag_type     text not null default 'URGENT',
  urgency       text not null default 'THIS_WEEK',  -- IMMEDIATE | THIS_WEEK | THIS_MONTH
  is_resolved   boolean not null default false,
  resolved_at   timestamptz
);
create index if not exists idx_flags_resolved on cipher_active_flags (is_resolved);

-- ============================================================
-- ACTIONS
-- ============================================================
create table if not exists cipher_action_items (
  id            uuid primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  title         text not null,
  description   text,
  priority      text not null default 'MEDIUM',  -- CRITICAL | HIGH | MEDIUM | LOW
  status        text not null default 'OPEN',    -- OPEN | IN_PROGRESS | DONE
  due_date      date,
  source_agent  text default 'manual',
  completed_at  timestamptz
);
create index if not exists idx_actions_status on cipher_action_items (status);

-- ============================================================
-- CLIENTS
-- ============================================================
create table if not exists cipher_clients (
  id                  uuid primary key default gen_random_uuid(),
  created_at          timestamptz not null default now(),
  name                text not null,
  company             text,
  email               text,
  phone               text,
  status              text not null default 'ACTIVE',  -- ACTIVE | PAUSED | COMPLETED | CHURNED
  contract_value      numeric(12,2),
  revenue_collected   numeric(12,2) default 0,
  outstanding_balance numeric(12,2) default 0,
  notes               text
);

-- ============================================================
-- CONTACTS
-- ============================================================
create table if not exists cipher_contacts (
  id                uuid primary key default gen_random_uuid(),
  created_at        timestamptz not null default now(),
  name              text not null,
  category          text not null default 'FRIEND',  -- FAMILY | FRIEND | CLIENT | VENDOR | PARTNER
  phone             text,
  email             text,
  cadence_days      int default 14,
  last_contact_date date,
  is_active         boolean not null default true,
  notes             text
);

-- ============================================================
-- PETS
-- ============================================================
create table if not exists cipher_pets (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  name            text not null,
  species         text not null,  -- Cat | Dog
  breed           text,
  birthdate       date,
  last_vet_visit  date,
  next_vet_due    date,
  is_active       boolean not null default true,
  notes           text
);

-- Seed Jay's pets
insert into cipher_pets (name, species, breed) values
  ('Milo', 'Cat', 'Long-hair'),
  ('Lula', 'Dog', 'Dutch Shepherd mix'),
  ('Remy', 'Dog', 'Whippet mix')
on conflict do nothing;

-- ============================================================
-- AI WATCH
-- ============================================================
create table if not exists cipher_ai_watch (
  id                    uuid primary key default gen_random_uuid(),
  created_at            timestamptz not null default now(),
  threat_level          text not null default 'YELLOW',  -- GREEN | YELLOW | ORANGE | RED | BLACK
  category              text not null default 'UNKNOWN', -- MISALIGNMENT | CAPABILITY_JUMP | COMPANY_RACE | GEOPOLITICAL | INFRASTRUCTURE | SOVEREIGNTY
  title                 text not null,
  description           text,
  source_url            text,
  cipher_recommendation text,
  is_active             boolean not null default true
);
create index if not exists idx_watch_active on cipher_ai_watch (is_active);

-- ============================================================
-- DEFCON
-- ============================================================
create table if not exists cipher_defcon (
  id           uuid primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  level        int not null default 5 check (level between 1 and 5),
  reason       text not null default 'Normal operations',
  triggered_by text default 'cipher_command',
  active       boolean not null default true,
  resolved_at  timestamptz
);
create index if not exists idx_defcon_active on cipher_defcon (active);

-- Seed initial DEFCON 5 (green)
insert into cipher_defcon (level, reason, triggered_by, active)
values (5, 'System initialized — normal operations', 'cipher_init', true)
on conflict do nothing;

-- ============================================================
-- PLAYBOOKS
-- ============================================================
create table if not exists cipher_playbooks (
  id           uuid primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  defcon_level int not null check (defcon_level between 1 and 5),
  title        text not null,
  steps        jsonb not null default '[]',
  priority     int default 0,
  is_active    boolean not null default true
);

-- ============================================================
-- SETTINGS
-- ============================================================
create table if not exists cipher_settings (
  id         uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  key        text not null unique,
  value      text
);

-- Seed version info
insert into cipher_settings (key, value) values ('cipher_version', '2.0')
on conflict (key) do update set value = excluded.value;
