"""Database persistence for scan sessions"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiosqlite

from reconpilot.core.models import Asset, Finding, ScanSession, Severity, Task, TaskStatus


class Database:
    """Synchronous database handler"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    target TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    progress REAL,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    error TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    discovered_by TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    score REAL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    host TEXT NOT NULL,
                    description TEXT,
                    discovered_by TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    evidence TEXT,
                    recommendations TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            conn.commit()

    def save_session(self, session: ScanSession) -> None:
        """Save a scan session to database"""
        with sqlite3.connect(self.db_path) as conn:
            # Save session
            conn.execute(
                """INSERT OR REPLACE INTO sessions (id, target, started_at, completed_at, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    session.id,
                    session.target,
                    session.started_at.isoformat(),
                    session.completed_at.isoformat() if session.completed_at else None,
                    json.dumps(session.metadata),
                ),
            )

            # Save tasks
            for task in session.tasks:
                conn.execute(
                    """INSERT OR REPLACE INTO tasks 
                       (id, session_id, name, description, status, progress, created_at, 
                        started_at, completed_at, error, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task.id,
                        session.id,
                        task.name,
                        task.description,
                        task.status.value,
                        task.progress,
                        task.created_at.isoformat(),
                        task.started_at.isoformat() if task.started_at else None,
                        task.completed_at.isoformat() if task.completed_at else None,
                        task.error,
                        json.dumps(task.metadata),
                    ),
                )

            # Save assets
            for asset in session.assets:
                conn.execute(
                    """INSERT OR REPLACE INTO assets 
                       (id, session_id, type, value, discovered_by, timestamp, score, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        asset.id,
                        session.id,
                        asset.type,
                        asset.value,
                        asset.discovered_by,
                        asset.timestamp.isoformat(),
                        asset.score,
                        json.dumps(asset.metadata),
                    ),
                )

            # Save findings
            for finding in session.findings:
                conn.execute(
                    """INSERT OR REPLACE INTO findings 
                       (id, session_id, severity, title, host, description, discovered_by, 
                        timestamp, evidence, recommendations, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        finding.id,
                        session.id,
                        finding.severity.value,
                        finding.title,
                        finding.host,
                        finding.description,
                        finding.discovered_by,
                        finding.timestamp.isoformat(),
                        finding.evidence,
                        json.dumps(finding.recommendations),
                        json.dumps(finding.metadata),
                    ),
                )

            conn.commit()

    def get_session(self, session_id: str) -> Optional[ScanSession]:
        """Load a session from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            session = ScanSession(
                id=row["id"],
                target=row["target"],
                started_at=datetime.fromisoformat(row["started_at"]),
                completed_at=datetime.fromisoformat(row["completed_at"])
                if row["completed_at"]
                else None,
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            )

            # Load tasks
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE session_id = ?", (session_id,)
            )
            for row in cursor:
                task = Task(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    status=TaskStatus(row["status"]),
                    progress=row["progress"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    started_at=datetime.fromisoformat(row["started_at"])
                    if row["started_at"]
                    else None,
                    completed_at=datetime.fromisoformat(row["completed_at"])
                    if row["completed_at"]
                    else None,
                    error=row["error"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
                session.tasks.append(task)

            # Load assets
            cursor = conn.execute(
                "SELECT * FROM assets WHERE session_id = ?", (session_id,)
            )
            for row in cursor:
                asset = Asset(
                    id=row["id"],
                    type=row["type"],
                    value=row["value"],
                    discovered_by=row["discovered_by"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    score=row["score"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
                session.assets.append(asset)

            # Load findings
            cursor = conn.execute(
                "SELECT * FROM findings WHERE session_id = ?", (session_id,)
            )
            for row in cursor:
                finding = Finding(
                    id=row["id"],
                    severity=Severity(row["severity"]),
                    title=row["title"],
                    host=row["host"],
                    description=row["description"],
                    discovered_by=row["discovered_by"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    evidence=row["evidence"],
                    recommendations=json.loads(row["recommendations"])
                    if row["recommendations"]
                    else [],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
                session.findings.append(finding)

            return session

    def get_sessions(self) -> list[ScanSession]:
        """Get all sessions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT id FROM sessions ORDER BY started_at DESC")
            sessions = []
            for row in cursor:
                session = self.get_session(row["id"])
                if session:
                    sessions.append(session)
            return sessions

    def delete_session(self, session_id: str) -> None:
        """Delete a session and all related data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM findings WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM assets WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM tasks WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()


class AsyncDatabase:
    """Asynchronous database handler"""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def init_schema(self) -> None:
        """Initialize database schema"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    target TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    metadata TEXT
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    progress REAL,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    error TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    discovered_by TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    score REAL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    host TEXT NOT NULL,
                    description TEXT,
                    discovered_by TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    evidence TEXT,
                    recommendations TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            await conn.commit()

    async def save_session(self, session: ScanSession) -> None:
        """Save a scan session to database"""
        async with aiosqlite.connect(self.db_path) as conn:
            # Save session
            await conn.execute(
                """INSERT OR REPLACE INTO sessions (id, target, started_at, completed_at, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    session.id,
                    session.target,
                    session.started_at.isoformat(),
                    session.completed_at.isoformat() if session.completed_at else None,
                    json.dumps(session.metadata),
                ),
            )

            # Save tasks
            for task in session.tasks:
                await conn.execute(
                    """INSERT OR REPLACE INTO tasks 
                       (id, session_id, name, description, status, progress, created_at, 
                        started_at, completed_at, error, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task.id,
                        session.id,
                        task.name,
                        task.description,
                        task.status.value,
                        task.progress,
                        task.created_at.isoformat(),
                        task.started_at.isoformat() if task.started_at else None,
                        task.completed_at.isoformat() if task.completed_at else None,
                        task.error,
                        json.dumps(task.metadata),
                    ),
                )

            # Save assets
            for asset in session.assets:
                await conn.execute(
                    """INSERT OR REPLACE INTO assets 
                       (id, session_id, type, value, discovered_by, timestamp, score, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        asset.id,
                        session.id,
                        asset.type,
                        asset.value,
                        asset.discovered_by,
                        asset.timestamp.isoformat(),
                        asset.score,
                        json.dumps(asset.metadata),
                    ),
                )

            # Save findings
            for finding in session.findings:
                await conn.execute(
                    """INSERT OR REPLACE INTO findings 
                       (id, session_id, severity, title, host, description, discovered_by, 
                        timestamp, evidence, recommendations, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        finding.id,
                        session.id,
                        finding.severity.value,
                        finding.title,
                        finding.host,
                        finding.description,
                        finding.discovered_by,
                        finding.timestamp.isoformat(),
                        finding.evidence,
                        json.dumps(finding.recommendations),
                        json.dumps(finding.metadata),
                    ),
                )

            await conn.commit()
