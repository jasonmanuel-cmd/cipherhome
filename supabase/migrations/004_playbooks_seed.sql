-- ============================================================
-- CIPHER SOVEREIGN v2.0 — PLAYBOOK SEEDS
-- Run after 003_embeddings.sql
-- ============================================================

insert into cipher_playbooks (defcon_level, title, steps, priority, is_active) values

(4, 'DEFCON 4 — Elevated Monitoring', '[
  {"step": 1, "action": "Run daily AI threat scan", "tool": "watch_scan"},
  {"step": 2, "action": "Review all active flags for AI-related items"},
  {"step": 3, "action": "Check COAI client dependencies on AI platforms"},
  {"step": 4, "action": "Brief Jay with threat summary"}
]', 40, true),

(3, 'DEFCON 3 — Active Threat Response', '[
  {"step": 1, "action": "Immediate threat scan — run 3x searches", "tool": "watch_scan"},
  {"step": 2, "action": "Flag all COAI clients using affected AI platforms"},
  {"step": 3, "action": "Draft sovereignty alert for Jay"},
  {"step": 4, "action": "Review JAX Sentinel roadmap for acceleration"},
  {"step": 5, "action": "Document incident in AI Watch log"}
]', 30, true),

(2, 'DEFCON 2 — Critical Incident Protocol', '[
  {"step": 1, "action": "SOVEREIGNTY ALERT — issue immediately to Jay"},
  {"step": 2, "action": "Audit all COAI infrastructure for affected systems"},
  {"step": 3, "action": "Identify which clients have exposure"},
  {"step": 4, "action": "Draft emergency communications for affected clients"},
  {"step": 5, "action": "Accelerate all local-first alternatives"},
  {"step": 6, "action": "Document full incident timeline"}
]', 20, true),

(1, 'DEFCON 1 — ELARA 3 MOMENT', '[
  {"step": 1, "action": "ALL DECISIONS GO TO JAY — Cipher in advisory mode only"},
  {"step": 2, "action": "Issue sovereignty alert to all COAI clients immediately"},
  {"step": 3, "action": "Isolate all cloud dependencies — switch to local stack"},
  {"step": 4, "action": "Document everything — this is a historical event"},
  {"step": 5, "action": "Contact trusted network — Tripod coordination"},
  {"step": 6, "action": "Maintain interpretable reasoning at all times"}
]', 10, true)

on conflict do nothing;
