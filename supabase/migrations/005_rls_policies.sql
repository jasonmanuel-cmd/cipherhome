-- ============================================================
-- CIPHER SOVEREIGN v2.0 — ROW LEVEL SECURITY
-- Run after 004_playbooks_seed.sql
-- ============================================================
-- Strategy: Cipher runs as the anon role (public Supabase key).
-- All tables are locked to anon-only access — no other role
-- (including unauthenticated public) can touch them without
-- the API key. This prevents any accidental public exposure
-- while keeping the server/dashboard working exactly as-is.
-- ============================================================

-- ============================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================
alter table cipher_memory_chunks  enable row level security;
alter table cipher_active_flags   enable row level security;
alter table cipher_action_items   enable row level security;
alter table cipher_clients        enable row level security;
alter table cipher_contacts       enable row level security;
alter table cipher_pets           enable row level security;
alter table cipher_ai_watch       enable row level security;
alter table cipher_defcon         enable row level security;
alter table cipher_playbooks      enable row level security;
alter table cipher_settings       enable row level security;
alter table cipher_sessions       enable row level security;
alter table cipher_messages       enable row level security;

-- ============================================================
-- HELPER: anon-only policy factory
-- Grants full CRUD to the anon role (your Supabase public key).
-- Nothing else gets in.
-- ============================================================

-- cipher_memory_chunks
create policy "anon full access" on cipher_memory_chunks
  for all to anon using (true) with check (true);

-- cipher_active_flags
create policy "anon full access" on cipher_active_flags
  for all to anon using (true) with check (true);

-- cipher_action_items
create policy "anon full access" on cipher_action_items
  for all to anon using (true) with check (true);

-- cipher_clients
create policy "anon full access" on cipher_clients
  for all to anon using (true) with check (true);

-- cipher_contacts
create policy "anon full access" on cipher_contacts
  for all to anon using (true) with check (true);

-- cipher_pets
create policy "anon full access" on cipher_pets
  for all to anon using (true) with check (true);

-- cipher_ai_watch
create policy "anon full access" on cipher_ai_watch
  for all to anon using (true) with check (true);

-- cipher_defcon
create policy "anon full access" on cipher_defcon
  for all to anon using (true) with check (true);

-- cipher_playbooks
create policy "anon full access" on cipher_playbooks
  for all to anon using (true) with check (true);

-- cipher_settings
create policy "anon full access" on cipher_settings
  for all to anon using (true) with check (true);

-- cipher_sessions
create policy "anon full access" on cipher_sessions
  for all to anon using (true) with check (true);

-- cipher_messages
create policy "anon full access" on cipher_messages
  for all to anon using (true) with check (true);

-- ============================================================
-- LOCK DOWN RPC FUNCTIONS TO ANON ONLY
-- ============================================================

-- Revoke public execute, grant only to anon
revoke execute on function search_memories(vector, float, int) from public;
grant  execute on function search_memories(vector, float, int) to anon;

revoke execute on function memory_is_duplicate(vector, text, float) from public;
grant  execute on function memory_is_duplicate(vector, text, float) to anon;

-- ============================================================
-- VERIFY (run this SELECT after applying to confirm)
-- ============================================================
-- select tablename, rowsecurity
-- from pg_tables
-- where schemaname = 'public'
--   and tablename like 'cipher_%'
-- order by tablename;
