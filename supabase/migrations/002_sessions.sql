-- ============================================================
-- CIPHER SOVEREIGN v2.0 — SESSION PERSISTENCE
-- Run after 001_initial_schema.sql
-- ============================================================

-- ============================================================
-- SESSIONS
-- ============================================================
create table if not exists cipher_sessions (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  title       text,
  is_active   boolean not null default true
);
create index if not exists idx_sessions_active on cipher_sessions (is_active, created_at desc);

-- ============================================================
-- MESSAGES
-- ============================================================
create table if not exists cipher_messages (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  session_id  uuid not null references cipher_sessions(id) on delete cascade,
  role        text not null,   -- user | assistant
  content     text not null,
  engine      text,
  tools_used  jsonb default '[]'
);
create index if not exists idx_messages_session on cipher_messages (session_id, created_at asc);
