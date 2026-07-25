# Nexa

A personal, voice-activated assistant. Wakes on "Hey Nexa," verifies it's
actually you speaking, and routes commands to local skill modules.

## Phase 0 status: Foundation ✅
- Config loading (`config.yaml`)
- Event bus (async pub-sub)
- Skill interface (`nexa/skills/base.py`)
- SQLite database with initial schema
- One test skill (`ping`) proving the whole pipeline fires correctly

## Running it (Phase 0)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m nexa.main
```

You should see logs showing: config loaded → database ready → a simulated
command → the ping skill responding "Pong. Nexa is alive."

## What's NOT built yet
- No voice input (Phase 1)
- No real orchestrator/LLM routing (Phase 2) — main.py fakes this for now
- No real skills besides the ping test (Phase 3+)

See `nexa-roadmap.md` for the full phased plan.

## Project layout
```
nexa/
├── nexa/
│   ├── config.py       Settings loader (reads config.yaml)
│   ├── event_bus.py    Async pub-sub connecting all components
│   ├── db.py            SQLite setup
│   ├── main.py           Entry point
│   └── skills/
│       ├── base.py       Skill interface every feature implements
│       └── ping.py       Throwaway test skill
├── config.yaml           Your personal settings
└── requirements.txt
```
