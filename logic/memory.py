"""
Core Memory with Letta (MemGPT) Integration for ET AI Concierge
----------------------------------------------------------------
Implements persistent cross-session memory so the agent remembers
the user's risk appetite, financial goals, and profile across sessions.

Phase 3 Task: Implement "Core Memory" persistence via Letta (MemGPT),
allowing the agent to remember the user's risk appetite across the session.

Architecture:
  - Primary:  Letta (MemGPT) for rich agentic memory (if installed)
  - Fallback: SQLite-based local persistence (always available)
  - In-memory dict used only as runtime cache
"""

import json
import sqlite3
import logging
import hashlib
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Try importing Letta (MemGPT) ─────────────────────────────────────────────
try:
    from letta_client import Letta, create_client, ChatMemory
    LETTA_AVAILABLE = True
except ImportError:
    LETTA_AVAILABLE = False
    logger.warning(
        "Letta/MemGPT not installed. Using SQLite persistence instead. "
        "Install with: pip install letta-client"
    )

# ── SQLite persistence path ───────────────────────────────────────────────────
DB_PATH = Path(__file__).parent.parent / "data" / "user_memory.db"


# ── SQLite Persistent Memory (fallback) ──────────────────────────────────────

class SQLiteMemoryStore:
    """SQLite-backed persistent memory store."""

    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                session_id   TEXT PRIMARY KEY,
                profile_json TEXT NOT NULL,
                updated_at   TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                event        TEXT NOT NULL,
                timestamp    TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save(self, session_id: str, profile: dict):
        now = datetime.utcnow().isoformat()
        self.conn.execute("""
            INSERT INTO user_profiles (session_id, profile_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                profile_json = excluded.profile_json,
                updated_at   = excluded.updated_at
        """, (session_id, json.dumps(profile), now))
        self.conn.execute("""
            INSERT INTO memory_log (session_id, event, timestamp)
            VALUES (?, ?, ?)
        """, (session_id, f"profile_saved: {profile}", now))
        self.conn.commit()
        logger.info(f"Profile saved to SQLite for session {session_id}")

    def load(self, session_id: str) -> dict:
        cur = self.conn.execute(
            "SELECT profile_json FROM user_profiles WHERE session_id = ?",
            (session_id,)
        )
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return {}

    def clear(self, session_id: str):
        self.conn.execute(
            "DELETE FROM user_profiles WHERE session_id = ?", (session_id,)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


# ── Letta (MemGPT) Memory (primary) ──────────────────────────────────────────

class LettaMemoryStore:
    """
    Letta (MemGPT) backed persistent memory.
    Stores user profile as structured Core Memory blocks
    so the agent can recall risk appetite, goals, and experience
    across any number of sessions.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.agent_id = f"et_concierge_{session_id[:8]}"
        try:
            self.client = create_client()
            # Check if agent already exists for this user
            existing = [a for a in self.client.list_agents() if a.name == self.agent_id]
            if existing:
                self.agent = existing[0]
                logger.info(f"Resumed Letta agent for session {session_id}")
            else:
                self.agent = self.client.create_agent(
                    name=self.agent_id,
                    memory=ChatMemory(
                        human="ET Concierge User",
                        persona=(
                            "I am the ET AI Concierge. I remember the user's "
                            "financial profile, risk appetite, and goals."
                        )
                    )
                )
                logger.info(f"Created new Letta agent for session {session_id}")
        except Exception as e:
            logger.error(f"Letta init failed: {e}")
            raise

    def save(self, profile: dict):
        """Store profile as a Core Memory update."""
        memory_text = (
            f"User Financial Profile (session {self.session_id}):\n"
            f"  Experience Level : {profile.get('type', 'unknown')}\n"
            f"  Financial Goal   : {profile.get('goal', 'unknown')}\n"
            f"  Risk Appetite    : {profile.get('risk', 'medium')}\n"
            f"  Saved At         : {datetime.utcnow().isoformat()}"
        )
        self.client.update_agent(
            agent_id=self.agent.id,
            memory=ChatMemory(human=memory_text, persona=self.agent.memory.persona)
        )
        logger.info("Profile saved to Letta Core Memory.")

    def load(self) -> dict:
        """Retrieve profile from Core Memory."""
        try:
            agent_state = self.client.get_agent(self.agent.id)
            human_block = agent_state.memory.human
            # Parse back structured data from memory text
            profile = {}
            for line in human_block.split("\n"):
                if "Experience Level" in line:
                    profile["type"] = line.split(":")[1].strip()
                elif "Financial Goal" in line:
                    profile["goal"] = line.split(":")[1].strip()
                elif "Risk Appetite" in line:
                    profile["risk"] = line.split(":")[1].strip()
            return profile
        except Exception as e:
            logger.error(f"Letta load failed: {e}")
            return {}


# ── UserMemory: unified interface ─────────────────────────────────────────────

class UserMemory:
    """
    Unified memory interface for ET AI Concierge.

    Tries Letta (MemGPT) first for rich persistent memory.
    Falls back to SQLite for reliable cross-session persistence.
    Also maintains an in-memory cache for fast access within a session.

    Usage:
        memory = UserMemory(session_id="user_abc123")
        memory.save_profile({"type": "beginner", "goal": "tax_saving", "risk": "low"})
        profile = memory.get_profile()
    """

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self._cache: dict = {}
        self._letta: LettaMemoryStore | None = None
        self._sqlite: SQLiteMemoryStore = SQLiteMemoryStore()

        # Try Letta first
        if LETTA_AVAILABLE:
            try:
                self._letta = LettaMemoryStore(session_id)
                # Pre-load any existing memory
                existing = self._letta.load()
                if existing:
                    self._cache.update(existing)
                    logger.info(f"Restored profile from Letta for session {session_id}")
            except Exception as e:
                logger.warning(f"Letta unavailable ({e}), using SQLite.")
                self._letta = None
        else:
            # Pre-load from SQLite
            existing = self._sqlite.load(session_id)
            if existing:
                self._cache.update(existing)
                logger.info(f"Restored profile from SQLite for session {session_id}")

    def save_profile(self, profile: dict):
        """Save user profile to persistent memory."""
        self._cache.update(profile)

        if self._letta:
            try:
                self._letta.save(self._cache)
                return
            except Exception as e:
                logger.warning(f"Letta save failed ({e}), falling back to SQLite.")

        self._sqlite.save(self.session_id, self._cache)

    def get_profile(self) -> dict:
        """Get the current user profile (from cache, loaded at init)."""
        return dict(self._cache)

    def update_field(self, key: str, value):
        """Update a single field and persist."""
        self._cache[key] = value
        self.save_profile(self._cache)

    def clear(self):
        """Clear all memory for this session."""
        self._cache = {}
        self._sqlite.clear(self.session_id)
        logger.info(f"Memory cleared for session {self.session_id}")

    def has_existing_profile(self) -> bool:
        """Returns True if a saved profile exists for this session."""
        return bool(self._cache)
