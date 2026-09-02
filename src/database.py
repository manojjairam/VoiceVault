import sqlite3
from datetime import datetime


DB_NAME = "data/VoiceVault.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    """
    Create all required database tables.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Stores published organizational content
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS published_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT,
            key_points TEXT,
            action_items TEXT,
            keywords TEXT,
            original_transcription TEXT,
            created_at TEXT NOT NULL,
            published_by TEXT,
            status TEXT DEFAULT 'Published'
        )
    """)

    # Stores organization members
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organization_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Stores deletion confirmations from members
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deletion_confirmations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            member_name TEXT NOT NULL,
            confirmed_at TEXT NOT NULL,
            UNIQUE(content_id, member_name),
            FOREIGN KEY(content_id) REFERENCES published_content(id)
        )
    """)

    conn.commit()
    conn.close()


def add_member(name):
    """
    Add an organization member.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO organization_members (name)
            VALUES (?)
            """,
            (name,)
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_members():
    """
    Get all organization members.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name FROM organization_members ORDER BY name"
    )

    members = cursor.fetchall()

    conn.close()

    return members


def publish_content(
    title,
    summary,
    key_points,
    action_items,
    keywords,
    original_transcription,
    published_by
):
    """
    Save extracted content as published organizational content.
    """

    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        """
        INSERT INTO published_content (
            title,
            summary,
            key_points,
            action_items,
            keywords,
            original_transcription,
            created_at,
            published_by,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            summary,
            key_points,
            action_items,
            keywords,
            original_transcription,
            created_at,
            published_by,
            "Published"
        )
    )

    content_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return content_id


def get_published_content():
    """
    Get all currently published organizational content.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            summary,
            key_points,
            action_items,
            keywords,
            original_transcription,
            created_at,
            published_by,
            status
        FROM published_content
        ORDER BY id DESC
        """
    )

    content = cursor.fetchall()

    conn.close()

    return content


def confirm_deletion(content_id, member_name):
    """
    Record a member's deletion confirmation.
    """

    conn = get_connection()
    cursor = conn.cursor()

    confirmed_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:
        cursor.execute(
            """
            INSERT INTO deletion_confirmations (
                content_id,
                member_name,
                confirmed_at
            )
            VALUES (?, ?, ?)
            """,
            (
                content_id,
                member_name,
                confirmed_at
            )
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_deletion_confirmations(content_id):
    """
    Get all members who confirmed deletion.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT member_name
        FROM deletion_confirmations
        WHERE content_id = ?
        """,
        (content_id,)
    )

    confirmations = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return confirmations


def can_delete_content(content_id):
    """
    Content can be deleted only when every organization
    member has confirmed deletion.
    """

    members = get_members()

    if not members:
        return False

    member_names = {
        member[1]
        for member in members
    }

    confirmations = set(
        get_deletion_confirmations(content_id)
    )

    return member_names.issubset(confirmations)


def delete_content(content_id):
    """
    Permanently delete content and its confirmations.
    This should only be called after can_delete_content()
    returns True.
    """

    if not can_delete_content(content_id):
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM deletion_confirmations
        WHERE content_id = ?
        """,
        (content_id,)
    )

    cursor.execute(
        """
        DELETE FROM published_content
        WHERE id = ?
        """,
        (content_id,)
    )

    conn.commit()
    conn.close()

    return True

