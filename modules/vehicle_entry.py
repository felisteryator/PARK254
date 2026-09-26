"""
Park254 - Vehicle Entry Module
Implements the Vehicle Entry algorithm from Task One, part (a):
- checks for duplicate active registration
- finds a free slot
- records the vehicle's details and starts a parking session
"""

from datetime import datetime
from database import get_connection
from modules import slot_management


def is_currently_parked(plate):
    """
    Checks active_records (ParkingSession rows with status ACTIVE) for this plate.
    This is the duplicate check we added earlier — prevents the same vehicle
    being registered twice while it's already parked.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM ParkingSession WHERE plate = ? AND status = 'ACTIVE'",
        (plate,)
    )
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def _save_vehicle(plate, full_name, phone_number, vehicle_type):
    """
    Inserts the vehicle if it's new, or updates contact details if this plate
    has parked before (e.g. phone number changed since last visit).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Vehicle WHERE plate = ?", (plate,))
    if cur.fetchone():
        cur.execute(
            "UPDATE Vehicle SET full_name = ?, phone_number = ?, vehicle_type = ? WHERE plate = ?",
            (full_name, phone_number, vehicle_type, plate)
        )
    else:
        cur.execute(
            "INSERT INTO Vehicle (plate, full_name, phone_number, vehicle_type) VALUES (?, ?, ?, ?)",
            (plate, full_name, phone_number, vehicle_type)
        )
    conn.commit()
    conn.close()


def register_entry(full_name, phone_number, vehicle_type, plate):
    """
    Matches registerEntry() from part (a).
    Returns a dict: {"success": bool, "message": str, "slot_id": int or None, "plate": str}
    """
    plate = plate.strip().upper().replace(" ", "")  # normalize so "KAA 123A", "kaa123a", "KAA123A" are all treated as the same plate

    if is_currently_parked(plate):
        return {"success": False, "message": "Vehicle already registered and currently parked", "slot_id": None, "plate": plate}

    slot_id = slot_management.find_free_slot()
    if slot_id is None:
        return {"success": False, "message": "No slots available. Please try another parking facility.", "slot_id": None, "plate": plate}

    _save_vehicle(plate, full_name, phone_number, vehicle_type)
    slot_management.occupy_slot(slot_id)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO ParkingSession (plate, slot_id, entry_time, status)
           VALUES (?, ?, ?, 'ACTIVE')""",
        (plate, slot_id, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()

    return {"success": True, "message": f"Vehicle registered at slot {slot_id}", "slot_id": slot_id, "plate": plate}