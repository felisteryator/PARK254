"""
Park254 - Slot Management Module
Implements the Slot Management algorithms from Task One, part (a).
Every other module reads or writes slot state through these functions.
"""

from database import get_connection


def find_free_slot():
    """
    Returns the slot_id of the first FREE slot, or None if the lot is full.
    Matches the findFreeSlot() algorithm from part (a).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT slot_id FROM Slot WHERE status = 'FREE' ORDER BY slot_id LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row["slot_id"] if row else None


def count_free_slots():
    """Returns how many slots are currently FREE."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS free_count FROM Slot WHERE status = 'FREE'")
    row = cur.fetchone()
    conn.close()
    return row["free_count"]


def count_total_slots():
    """Returns the total number of slots in the lot."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM Slot")
    row = cur.fetchone()
    conn.close()
    return row["total"]


def get_all_slots():
    """
    Returns every slot with its status, ordered by slot_id.
    This is what the Display Module (and the driver-facing homepage) reads from.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT slot_id, status FROM Slot ORDER BY slot_id")
    rows = cur.fetchall()
    conn.close()
    return [{"slot_id": r["slot_id"], "status": r["status"]} for r in rows]


def occupy_slot(slot_id):
    """Marks a slot as OCCUPIED. Called by Vehicle Entry once a vehicle is assigned to it."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Slot SET status = 'OCCUPIED' WHERE slot_id = ?", (slot_id,))
    conn.commit()
    conn.close()


def free_slot(slot_id):
    """Marks a slot as FREE. Called by Payment & Exit once a vehicle leaves."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Slot SET status = 'FREE' WHERE slot_id = ?", (slot_id,))
    conn.commit()
    conn.close()


def add_slots(number_to_add):
    """
    Admin function: increases parking capacity by adding new slots.
    Safe to call any time — appends new slot_ids after the current highest one,
    so existing slots (and any vehicles currently parked) are never disturbed.
    Returns the new total slot count.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(MAX(slot_id), 0) AS max_id FROM Slot")
    current_max = cur.fetchone()["max_id"]

    new_ids = range(current_max + 1, current_max + 1 + number_to_add)
    cur.executemany(
        "INSERT INTO Slot (slot_id, status) VALUES (?, 'FREE')",
        [(i,) for i in new_ids]
    )
    conn.commit()

    count_cur = conn.cursor()
    count_cur.execute("SELECT COUNT(*) AS total FROM Slot")
    new_total = count_cur.fetchone()["total"]
    conn.close()
    return new_total

