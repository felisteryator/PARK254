"""
Park254 - Payment & Exit Module
Implements the processExit() algorithm from Task One, part (a).
No waiting queue — freeing a slot here just makes it available for the next
driver who walks up, rather than pulling anyone in automatically.
"""

from datetime import datetime
from database import get_connection
from modules import fee_calculation, slot_management


def open_barrier():
    """
    Placeholder for the physical/simulated barrier control.
    In a real deployment this would send a signal to hardware;
    here it just represents the action for the web-based system.
    """
    print("Barrier opening...")


def process_exit(plate, amount_paid):
    """
    Matches processExit() from part (a).
    Returns {"success": bool, "message": str, "duration_minutes": int or None,
             "fee": float or None, "entry_time": str or None, "exit_time": str or None}
    """
    plate = plate.strip().upper().replace(" ", "")

    session = fee_calculation.get_active_session(plate)
    if session is None:
        return {"success": False, "message": "Vehicle not found in parking. Exit denied.",
                "duration_minutes": None, "fee": None, "entry_time": None, "exit_time": None}

    fee_result = fee_calculation.calculate_fee(plate)
    duration_minutes = fee_result["duration_minutes"]
    fee = fee_result["fee"]
    entry_time = session["entry_time"]

    if amount_paid < fee:
        return {"success": False, "message": f"Insufficient payment. Amount due: Kshs. {fee}",
                "duration_minutes": duration_minutes, "fee": fee, "entry_time": entry_time, "exit_time": None}

    open_barrier()

    exit_time = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE ParkingSession
        SET exit_time = ?, fee_charged = ?, status = 'COMPLETED'
        WHERE session_id = ?
    """, (exit_time, fee, session["session_id"]))
    conn.commit()
    conn.close()

    slot_management.free_slot(session["slot_id"])

    return {
        "success": True,
        "message": f"Exit approved. Time: {duration_minutes} min, Paid: Kshs. {fee}",
        "duration_minutes": duration_minutes,
        "fee": fee,
        "entry_time": entry_time,
        "exit_time": exit_time
    }