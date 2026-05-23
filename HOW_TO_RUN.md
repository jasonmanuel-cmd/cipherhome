# CIPHER SOVEREIGN v2.0 — HOW TO RUN

Everything you need to get from zero to fully operational.

---

## BEFORE YOU START — One-Time Setup

### Step 1 · Install Ollama

Download from https://ollama.com and install it.
After install, open PowerShell and verify:
```powershell
ollama --version
```

Pull the default fast model (2GB, runs on any CPU):
```powershell
ollama pull llama3.2:3b
```

Optional — pull the deep-think model (5GB, needs 8GB+ RAM):
```powershell
ollama pull deepseek-r1:8b
```

Optional — pull the embedding model for smart memory search (274MB):
```powershell
ollama pull nomic-embed-text
```

---

### Step 2 · Install Python dependencies

Open PowerShell in the Cipher folder:
```powershell
cd C:\Users\blunt\Cipher
pip install -r requirements.txt
```

---

### Step 3 · Run Supabase migrations

Open your Supabase project at https://supabase.com/dashboard
→ Select project `expcinwdxxlfgkuxpirq`
→ Click **SQL Editor** in the left sidebar
→ Paste and run each file IN ORDER:

1. `supabase/migrations/001_initial_schema.sql`
2. `supabase/migrations/002_sessions.sql`
3. `supabase/migrations/003_embeddings.sql`
4. `supabase/migrations/004_playbooks_seed.sql`
5. `supabase/migrations/005_rls_policies.sql`

Each one should say "Success. No rows returned."

---

### Step 4 · Configure .env (optional)

The defaults work out of the box for local use. Edit `.env` only if you want:
- Cloud fallback: set `ANTHROPIC_API_KEY=sk-ant-...`
- API key protection: set `CIPHER_API_KEY=your_secret`

---

## EVERY DAY — Starting Cipher

### Option A: PowerShell launcher (recommended)

Right-click `cipher_launch.ps1` → **Run with PowerShell**

It automatically:
- Starts Ollama if not running
- Pulls a model if none installed
- Installs Python deps
- Launches the server
- Opens the dashboard in your browser

---

### Option B: Manual (2 terminals)

**Terminal 1 — Start Ollama:**
```powershell
ollama serve
```

**Terminal 2 — Start Cipher:**
```powershell
cd C:\Users\blunt\Cipher
python cipher_server.py
```

Then open your browser to: **http://localhost:3131**

---

## USING THE DASHBOARD

### Chat (⚡ CMD)
- Type your message and hit Enter or click ➤
- Press 🎤 to speak instead of type
- Toggle 🔊 to have Cipher speak responses aloud
- **CONTINUOUS** mode keeps the mic open after each response
- **+ NEW CHAT** starts a fresh session (old one is archived)
- **↓ EXPORT** saves the conversation as Markdown, JSON, or text
- ENGINE selector (top bar): LOCAL = Ollama, CLOUD = Claude API, AUTO = tries local first

### Flags (🚨 FLAG)
Active alerts and sovereignty watches. Add flags, resolve them when done.

### Actions (✅ ACT)
Your tactical queue. Set priority and due dates. Mark done when complete.

### Clients (💼 CLT)
Revenue tracker. Shows active clients, contract value, collected, outstanding.

### Contacts (👤 CRM)
Relationship cadence tracker. Highlights overdue contacts.

### AI Watch (🛡 WATCH)
- DEFCON level (1=black, 5=green) with escalate/stand-down buttons
- Log threats manually or run **⟳ LIVE SCAN** for real-time web intelligence
- When you escalate DEFCON, Cipher shows the response playbook in chat

### Pets (🐾 PETS)
Milo, Lula, Remy health records. Log vet visits, track next due dates.

### Memory (🧠 MEM)
Search and log Cipher's persistent memory. Every chat auto-saves here.
If `nomic-embed-text` is installed, search is semantic (AI-powered).

### Settings (⚙ SET)
- Change Ollama URL, server port, model, API keys without editing .env
- Changes save to localStorage and apply immediately
- Pull missing models with one click
- Export conversation from here too

---

## VERIFY EVERYTHING IS WORKING

Open http://localhost:3131 — you should see the dashboard.

Check the top-left status indicator:
- 🟢 Green dot + model name = fully operational
- 🟡 Yellow = server up but no model loaded yet
- 🔴 Red = server not running

Click **⚙ SET** in the sidebar → System Info section shows:
```
ENGINE: llama3.2:3b
OLLAMA: ONLINE
CLOUD FALLBACK: DISABLED (or ENABLED if key set)
SEMANTIC MEMORY: ACTIVE — nomic-embed-text (or OFF)
AUTH: OPEN (local mode)
MODELS INSTALLED: llama3.2:3b, ...
```

Run the test suite to verify the server code is healthy:
```powershell
cd C:\Users\blunt\Cipher
python -m pytest tests/ -q
```
Should say: `84 passed`

---

## TROUBLESHOOTING

| Problem | Fix |
|---------|-----|
| Red dot / SERVER NOT RUNNING | Run `python cipher_server.py` in PowerShell |
| Model not loading | Run `ollama pull llama3.2:3b` |
| Ollama offline | Run `ollama serve` |
| Supabase errors in memory/flags | Run the 5 SQL migrations in Supabase SQL Editor |
| Voice mic not working | Must use Chrome or Edge (Firefox doesn't support Web Speech API) |
| Cloud fallback not working | Set `ANTHROPIC_API_KEY` in `.env` |
| Semantic memory showing OFF | Run `ollama pull nomic-embed-text` then restart server |
| Settings not saving | Dashboard uses localStorage — clear browser data if corrupt |

---

## FILE MAP

```
C:\Users\blunt\Cipher\
├── cipher_server.py              ← FastAPI backend (run this)
├── cipher_command_center_v2.html ← Dashboard (served at localhost:3131)
├── cipher_launch.ps1             ← One-click Windows launcher
├── .env                          ← Config (API keys, URLs, ports)
├── requirements.txt              ← Python dependencies
├── MODELS.md                     ← Model selection guide
├── HOW_TO_RUN.md                 ← This file
├── supabase/migrations/
│   ├── 001_initial_schema.sql    ← All 12 tables
│   ├── 002_sessions.sql          ← Chat session persistence
│   ├── 003_embeddings.sql        ← Vector search (pgvector)
│   ├── 004_playbooks_seed.sql    ← DEFCON response playbooks
│   └── 005_rls_policies.sql      ← Row Level Security
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_chat.py
    ├── test_memory.py
    ├── test_self_repair.py
    ├── test_status.py
    ├── test_tools.py
    └── test_watch.py
```

---

## CIPHER IS NOW 100% OPERATIONAL.
