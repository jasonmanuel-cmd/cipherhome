-- ============================================================
-- CIPHER SOVEREIGN v2.0 — VECTOR EMBEDDINGS
-- Run after 002_sessions.sql
-- Requires pgvector (enabled by default on Supabase)
-- ============================================================

-- Enable pgvector
create extension if not exists vector;

-- Add embedding column to memory chunks (nomic-embed-text = 768 dims)
alter table cipher_memory_chunks
  add column if not exists embedding vector(768);

-- Index for fast cosine similarity search
create index if not exists idx_memory_embedding
  on cipher_memory_chunks
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- ============================================================
-- SEMANTIC SEARCH FUNCTION
-- Called via Supabase RPC: POST /rest/v1/rpc/search_memories
-- ============================================================
create or replace function search_memories(
  query_embedding vector(768),
  match_threshold float default 0.75,
  match_count     int     default 5
)
returns table (
  id               uuid,
  content          text,
  summary          text,
  category         text,
  source           text,
  created_at       timestamptz,
  similarity       float
)
language sql stable
as $$
  select
    id,
    content,
    summary,
    category,
    source,
    created_at,
    1 - (embedding <=> query_embedding) as similarity
  from cipher_memory_chunks
  where
    is_active = true
    and embedding is not null
    and 1 - (embedding <=> query_embedding) > match_threshold
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- ============================================================
-- DEDUP FUNCTION — returns true if near-duplicate exists
-- ============================================================
create or replace function memory_is_duplicate(
  check_embedding vector(768),
  check_category  text,
  similarity_threshold float default 0.92
)
returns boolean
language sql stable
as $$
  select exists (
    select 1 from cipher_memory_chunks
    where
      is_active = true
      and category = check_category
      and embedding is not null
      and 1 - (embedding <=> check_embedding) > similarity_threshold
      and created_at > now() - interval '7 days'
  );
$$;
