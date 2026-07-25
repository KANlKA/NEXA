#setting up a local SQLite local db.
#QLite is just a single file on disk, no server to run, which fits a local-first personal assistant.

import sqlite3
from nexa.config import get_config

#includes commands_log, cache_exact, memory_facts tables.
SCHEMA = """
CREATE TABLE IF NOT EXISTS commands_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_text TEXT NOT NULL,
    intent TEXT,
    skill_used TEXT,
    success INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cache_exact (
    command_hash TEXT PRIMARY KEY,
    raw_text TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity TEXT NOT NULL,
    value TEXT NOT NULL,
    tags TEXT,
    source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def get_connection() -> sqlite3.Connection:
    """
    Opens a connection to Nexa's database file (creating it if needed)
    and makes sure the schema above exists.
    """
    cfg = get_config()
    conn = sqlite3.connect(cfg.db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
