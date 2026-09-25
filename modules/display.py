"""
Park254 - Display Module
Implements getAvailabilityView() from Task One, part (a).
This module owns no data of its own — it reads directly from Slot Management,
which is exactly why it stays this thin.
"""

from modules import slot_management


def get_availability_view():
    """
    Returns everything the driver-facing homepage needs:
    free count, total count, and the full per-slot grid.
    """
    free = slot_management.count_free_slots()
    total = slot_management.count_total_slots()
    slots = slot_management.get_all_slots()
    return {
        "free": free,
        "total": total,
        "slots": slots
    }
