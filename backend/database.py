
import sqlite3
import uuid
from datetime import datetime

DATABASE = "k_memory.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()


def create_conversation():
    conversation_id = str(uuid.uuid4())

    conn = get_connection()
    conn.execute(
        "INSERT INTO conversations VALUES (?, ?)",
        (conversation_id, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return conversation_id


def conversation_exists(conversation_id):
    conn = get_connection()

    result = conn.execute(
        "SELECT id FROM conversations WHERE id = ?",
        (conversation_id,)
    ).fetchone()

    conn.close()
    return result is not None


def save_message(conversation_id, role, content):
    conn = get_connection()

    conn.execute("""
        INSERT INTO messages
        (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        conversation_id,
        role,
        content,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_messages(conversation_id):
    conn = get_connection()

    rows = conn.execute("""
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
    """, (conversation_id,)).fetchall()

    conn.close()

    return [
        {"role": row["role"], "content": row["content"]}
        for row in rows
    ]
