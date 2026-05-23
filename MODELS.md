# CIPHER SOVEREIGN — MODEL UPGRADE GUIDE
# Best local models ranked for Cipher's use case

## TIER 1 — SOVEREIGN ELITE (Best reasoning, Jay's use case)

### DeepSeek R1:32B — THE RECOMMENDATION
ollama pull deepseek-r1:32b
- VRAM:   ~20GB (needs GPU with 24GB or CPU with 32GB RAM)
- Speed:  Moderate (10-30 tok/s on good GPU)
- Why:    Chain-of-thought reasoning. Thinks before answering.
          Best for: strategy, business decisions, architecture review
          DeepSeek R1 is the model referenced — this is it.

### DeepSeek R1:14B — BEST BALANCE
ollama pull deepseek-r1:14b
- VRAM:   ~9GB (RTX 3080/4070 class)
- Speed:  Fast
- Why:    90% of 32B quality at half the size. Recommended for Jay's HP.

### DeepSeek R1:8B — FAST CIPHER
ollama pull deepseek-r1:8b
- VRAM:   ~5GB (any modern GPU)
- Speed:  Very fast (40+ tok/s)
- Why:    Instant responses. Good enough for 80% of queries.

---

## TIER 2 — GENERAL POWERHOUSE

### Llama 3.3:70B — META'S BEST
ollama pull llama3.3:70b
- RAM:    ~40GB (CPU inference only unless you have A100)
- Speed:  Slow on CPU (~3-5 tok/s)
- Why:    Strongest general model if you have the hardware

### Qwen 2.5:32B — STRONG ALL-ROUNDER
ollama pull qwen2.5:32b
- VRAM:   ~18GB
- Speed:  Good
- Why:    Strong coding + reasoning. Good Cipher alternative.

### Mistral:7B — SPEED DEMON
ollama pull mistral:latest
- VRAM:   ~4GB
- Speed:  Blazing fast
- Why:    Quick lookups, fast commands. Not deep reasoning.

---

## RECOMMENDED SETUP FOR JAY'S HP DESKTOP

Check your GPU first:
  nvidia-smi        (Windows PowerShell)
  nvidia-smi -L     (list GPUs)

If you have:
  RTX 3060 (12GB):  deepseek-r1:8b + qwen2.5:7b
  RTX 3080 (10GB):  deepseek-r1:8b
  RTX 4070 (12GB):  deepseek-r1:14b  ← SWEET SPOT
  RTX 4080 (16GB):  deepseek-r1:14b + qwen2.5:14b
  RTX 4090 (24GB):  deepseek-r1:32b  ← FULL POWER
  No GPU / CPU:     deepseek-r1:8b (slow but works)

---

## PULL COMMANDS (run in PowerShell or WSL2)

# Minimum viable Cipher (any machine)
ollama pull deepseek-r1:8b

# Recommended Cipher setup
ollama pull deepseek-r1:14b
ollama pull mistral:latest

# Maximum Cipher (24GB+ VRAM)
ollama pull deepseek-r1:32b
ollama pull qwen2.5:32b

# Embeddings (for true semantic memory search — future upgrade)
ollama pull nomic-embed-text
ollama pull mxbai-embed-large

---

## CHECK WHAT YOU HAVE

ollama list                    # list installed models
ollama ps                      # show running models
nvidia-smi                     # GPU memory usage
curl http://localhost:11434/api/tags  # API check

---

## CIPHER ENGINE MODES (in dashboard)

LOCAL  — Uses best available Ollama model. Sovereign. No data leaves machine.
CLOUD  — Uses Claude API (claude-sonnet-4-20250514). Best quality. Data leaves machine.
AUTO   — Tries local first, falls back to cloud. Best of both.

⚠ SOVEREIGNTY NOTE: LOCAL mode is pure sovereign infrastructure.
  All data stays on your machine. Zero external calls except Supabase (your data).
  CLOUD mode sends your queries to Anthropic servers.
  For sensitive ops, use LOCAL mode.
