"""
Park254 - Fee Calculation Module
Implements the calculateFee() algorithm from Task One, part (a).
Pricing tiers are read from the FeeTier table (part c) rather than hardcoded,
so the client can change prices later without touching code.
"""

from datetime import datetime
from database import get_connection


def get_active_session(plate):
    """
    Returns the active ParkingSession row for this plate, or None if not parked.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM ParkingSession WHERE plate = ? AND status = 'ACTIVE'",
        (plate,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def calculate_fee(plate):
    """
    Computes how long the vehicle has been parked and what it owes,
    based on entry_time and the FeeTier table.

    Returns {"success": bool, "message": str, "duration_minutes": int or None, "fee": float or None}
    """
    session = get_active_session(plate)
    if session is None:
        return {"success": False, "message": "Vehicle not found in parking.",
                "duration_minutes": None, "fee": None}

    entry_time = datetime.fromisoformat(session["entry_time"])
    duration_minutes = (datetime.now() - entry_time).total_seconds() / 60
    duration_minutes = max(0, round(duration_minutes))  # never negative, whole minutes

    conn = get_connection()
    cur = conn.cursor()
    # Tiers are ordered ascending by max_minutes — first tier the duration fits under wins.
    cur.execute("SELECT max_minutes, fee FROM FeeTier ORDER BY max_minutes ASC")
    tiers = cur.fetchall()
    conn.close()

    fee = None
    for tier in tiers:
        if duration_minutes <= tier["max_minutes"]:
            fee = tier["fee"]
            break

    if fee is None:
        # Safety net in case duration exceeds every tier (shouldn't happen with a proper sentinel tier)
        fee = tiers[-1]["fee"] if tiers else 0

    return {"success": True, "message": "Fee calculated", "duration_minutes": duration_minutes, "fee": fee}