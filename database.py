"""
Park254 - Database Module
Implements the schema designed in Task One, part (c).
Uses SQLite so no separate database server is needed.
"""

import sqlite3

DB_NAME = "parking.db"

# Default fee tiers, taken from the client's pricing table.
# Stored as data (not hardcoded logic) so prices can change without touching code.
DEFAULT_FEE_TIERS = [
    (1, 30, 0),        # up to 30 minutes: free
    (2, 120, 50),       # up to 2 hours: Kshs. 50
    (3, 240, 100),      # up to 4 hours: Kshs. 100
    (4, 360, 300),      # up to 6 hours: Kshs. 300
    (5, 999999, 500),   # over 6 hours: Kshs. 500
]

TOTAL_SLOTS = 10  # adjust to however many slots the parking lot actually has


def get_connection():
    """Returns a new database connection. Each Flask request should get its own."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row   # lets us access columns by name, e.g. row["plate"]
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite disables FK enforcement by default
    return conn


def init_db():
    """Creates all tables (if they don't already exist) and seeds default data."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Slot (
            slot_id     INTEGER PRIMARY KEY,
            status      TEXT NOT NULL CHECK (status IN ('FREE', 'OCCUPIED'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Vehicle (
            plate           TEXT PRIMARY KEY,
            full_name       TEXT NOT NULL,
            phone_number    TEXT NOT NULL,
            email           TEXT,
            vehicle_type    TEXT
        )
    """)

    # Migration: add vehicle_type to a Vehicle table created before this column existed.
    cur.execute("PRAGMA table_info(Vehicle)")
    existing_vehicle_columns = [row[1] for row in cur.fetchall()]
    if "vehicle_type" not in existing_vehicle_columns:
        cur.execute("ALTER TABLE Vehicle ADD COLUMN vehicle_type TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ParkingSession (
            session_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            plate           TEXT NOT NULL REFERENCES Vehicle(plate),
            slot_id         INTEGER REFERENCES Slot(slot_id),
            entry_time      TEXT NOT NULL,
            exit_time       TEXT,
            fee_charged     REAL,
            payment_method  TEXT,
            status          TEXT NOT NULL CHECK (status IN ('ACTIVE', 'COMPLETED'))
        )
    """)

    # Migration: add payment_method to a ParkingSession table created before this column existed.
    cur.execute("PRAGMA table_info(ParkingSession)")
    existing_columns = [row[1] for row in cur.fetchall()]
    if "payment_method" not in existing_columns:
        cur.execute("ALTER TABLE ParkingSession ADD COLUMN payment_method TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS FeeTier (
            tier_id         INTEGER PRIMARY KEY,
            max_minutes     INTEGER NOT NULL,
            fee             REAL NOT NULL
        )
    """)

    # Seed slots only if the table is empty (avoid resetting state on every restart)
    cur.execute("SELECT COUNT(*) FROM Slot")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO Slot (slot_id, status) VALUES (?, 'FREE')",
            [(i,) for i in range(1, TOTAL_SLOTS + 1)]
        )

    # Seed fee tiers only if empty
    cur.execute("SELECT COUNT(*) FROM FeeTier")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO FeeTier (tier_id, max_minutes, fee) VALUES (?, ?, ?)",
            DEFAULT_FEE_TIERS
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Running this file directly sets up (or resets) the database.
    init_db()
    print(f"Database initialized: {DB_NAME} with {TOTAL_SLOTS} slots and default fee tiers.")