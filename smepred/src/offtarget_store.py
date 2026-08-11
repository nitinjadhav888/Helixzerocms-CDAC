"""
offtarget_store.py -- Persistent Cross-Process Off-Target Result Store
======================================================================
Provides a zero-ops, file-backed SQLite key-value store for off-target
safety dossiers, keyed by candidate antisense sequence hash.
Ensures safety results survive process restarts and can be shared.
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "offtarget_cache.db"


class OffTargetKVStore:
    """Persistent SQLite key-value store for off-target safety dossiers."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
        except Exception:
            pass
        return conn

    def _init_db(self) -> None:
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS off_target_cache (
                        key TEXT NOT NULL,
                        version TEXT NOT NULL DEFAULT 'GRCh38.p14',
                        data_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (key, version)
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize off-target SQLite store: {e}")

    def get(self, key: str, version: str = "GRCh38.p14") -> Optional[Dict[str, Any]]:
        """Retrieves cached off-target safety report for a sequence key and assembly version."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT data_json FROM off_target_cache WHERE key = ? AND version = ?", (key, version))
                row = cursor.fetchone()
                if row:
                    return json.loads(row["data_json"])
        except Exception as e:
            logger.warning(f"OffTargetKVStore get error for key '{key}': {e}")
        return None

    def set(self, key: str, value: Dict[str, Any], version: str = "GRCh38.p14") -> None:
        """Stores off-target safety report in persistent SQLite database."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO off_target_cache (key, version, data_json) VALUES (?, ?, ?)",
                    (key, version, json.dumps(value))
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"OffTargetKVStore set error for key '{key}': {e}")
