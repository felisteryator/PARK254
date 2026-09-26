"""
Park254 - Reporting/Admin Module
The optional module we flagged in Task One's module breakdown — not required
by the client brief's core requirements, but a reasonable addition for
operational oversight (viewing history, adjusting capacity).
"""

from database import get_connection
from modules import slot_management


def get_active_sessions():
    """
    Returns every vehicle currently parked (status ACTIVE), joined with
    their contact details, ordered by slot number. This is the
    'who is on-site right now, and where' view — admin-only, since it
    carries personal data (name, phone, plate) tied to a live location.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ParkingSession.session_id, ParkingSession.plate, Vehicle.full_name,
               Vehicle.phone_number, ParkingSession.slot_id, ParkingSession.entry_time
        FROM ParkingSession
        JOIN Vehicle ON Vehicle.plate = ParkingSession.plate
        WHERE ParkingSession.status = 'ACTIVE'
        ORDER BY ParkingSession.slot_id ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_session_history(limit=50):
    """
    Returns the most recent COMPLETED parking sessions, newest first,
    joined with the vehicle's contact details.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ParkingSession.session_id, ParkingSession.plate, Vehicle.full_name,
               ParkingSession.slot_id, ParkingSession.entry_time, ParkingSession.exit_time,
               ParkingSession.fee_charged, ParkingSession.payment_method
        FROM ParkingSession
        JOIN Vehicle ON Vehicle.plate = ParkingSession.plate
        WHERE ParkingSession.status = 'COMPLETED'
        ORDER BY ParkingSession.exit_time DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_total_revenue():
    """Sum of fees charged across all completed sessions — quick oversight figure."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(fee_charged), 0) AS total FROM ParkingSession WHERE status = 'COMPLETED'")
    total = cur.fetchone()["total"]
    conn.close()
    return total


def get_fee_tiers():
    """
    Returns every fee tier, ordered by max_minutes ascending — the same
    order the Fee Calculation Module reads them in.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tier_id, max_minutes, fee FROM FeeTier ORDER BY max_minutes ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_fee_tiers(tier_updates):
    """
    Updates the max_minutes and fee for a set of tiers in one go.
    tier_updates: list of dicts like [{"tier_id": 1, "max_minutes": 30, "fee": 0}, ...]

    Validates that max_minutes is strictly increasing across tiers before writing
    anything — an out-of-order bracket (e.g. tier 2's cutoff lower than tier 1's)
    would silently break the calculateFee() lookup, so we catch it here instead.
    """
    if not tier_updates:
        return {"success": False, "message": "No rate data received."}

    sorted_updates = sorted(tier_updates, key=lambda t: t["tier_id"])
    previous_max = -1
    for tier in sorted_updates:
        if tier["max_minutes"] <= previous_max:
            return {"success": False,
                    "message": "Each tier's time limit must be greater than the one before it."}
        if tier["fee"] < 0:
            return {"success": False, "message": "Fees cannot be negative."}
        previous_max = tier["max_minutes"]

    conn = get_connection()
    cur = conn.cursor()
    for tier in sorted_updates:
        cur.execute(
            "UPDATE FeeTier SET max_minutes = ?, fee = ? WHERE tier_id = ?",
            (tier["max_minutes"], tier["fee"], tier["tier_id"])
        )
    conn.commit()
    conn.close()

    return {"success": True, "message": "Parking rates updated."}


def expand_capacity(number_to_add):
    """
    Thin wrapper around Slot Management's add_slots(), so the admin page
    only needs to import this Reporting/Admin module, not reach into
    Slot Management directly.
    """
    if number_to_add <= 0:
        return {"success": False, "message": "Enter a number greater than zero.", "new_total": None}

    new_total = slot_management.add_slots(number_to_add)
    return {"success": True, "message": f"Added {number_to_add} slot(s).", "new_total": new_total}