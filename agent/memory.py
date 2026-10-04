"""
memory.py — Histórico persistente de conversas em SQLite.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import re

# O banco fica na raiz do projeto
DB_PATH = Path(__file__).parent.parent / "history.db"


def _connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas se não existirem."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                backend TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON conversations(created_at)")


def new_session_id() -> str:
    """Gera um ID único para a sessão atual."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_message(session_id: str, role: str, content: str, backend: str = None):
    """Salva uma mensagem (user ou assistant)."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations (session_id, role, content, backend) "
            "VALUES (?, ?, ?, ?)",
            (session_id, role, content, backend)
        )


def get_session_history(session_id: str, limit: int = 20):
    """Últimas N mensagens da sessão atual (ordem cronológica)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content, created_at FROM conversations "
            "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
    return list(reversed(rows))


def get_recent_from_other_sessions(current_session_id: str, limit: int = 5):
    """Últimas N mensagens de OUTRAS sessões, excluindo backend local (privacidade)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content, backend, created_at FROM conversations "
            "WHERE session_id != ? "
            "AND (backend IS NULL OR backend != 'local') "
            "ORDER BY id DESC LIMIT ?",
            (current_session_id, limit)
        ).fetchall()
    return list(reversed(rows))


def search(term: str, limit: int = 10):
    """Busca por termo no conteúdo das mensagens."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT session_id, role, content, created_at FROM conversations "
            "WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{term}%", limit)
        ).fetchall()
    return rows


def clear_all():
    """Apaga todo o histórico."""
    with _connect() as conn:
        conn.execute("DELETE FROM conversations")


def count_messages() -> int:
    """Quantas mensagens existem no banco."""
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM conversations").fetchone()
    return row["c"] if row else 0

import re

# Padrões a redigir
_REDACT_PATTERNS = [
    # "Senha gerada (N caracteres): xxxxx"
    (re.compile(r"(Senha gerada \(\d+ caracteres\):\s*)\S+"), r"\1[REDIGIDO]"),
    # Hash explícito
    (re.compile(r"(Hash \w+:\s*)[a-fA-F0-9]{16,}"), r"\1[REDIGIDO]"),
    # Caminhos de chave .key
    (re.compile(r"([\w\-]+\.key)"), r"[REDIGIDO].key"),
]


def redact_sensitive(text: str) -> str:
    """Substitui padrões sensíveis por [REDIGIDO]."""
    if not text:
        return text
    for pattern, replacement in _REDACT_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def get_recent_from_other_sessions(current_session_id: str, limit: int = 5):
    """Últimas N mensagens de OUTRAS sessões, com redação de segredos."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content, backend, created_at FROM conversations "
            "WHERE session_id != ? ORDER BY id DESC LIMIT ?",
            (current_session_id, limit)
        ).fetchall()
    # Aplica redação
    cleaned = []
    for row in reversed(rows):
        cleaned.append({
            "role": row["role"],
            "content": redact_sensitive(row["content"]),
            "backend": row["backend"],
            "created_at": row["created_at"],
        })
    return cleaned