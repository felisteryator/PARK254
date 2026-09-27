# Task One — Part (a): Module Algorithms

Park254 is broken into six modules, each with a clear responsibility. The
algorithms below are written as pseudocode and correspond directly to the
Python implementation in `modules/`.

## 1. Slot Management Module

Owns the state of every physical slot (FREE / OCCUPIED). Every other module
reads or writes slot state through this module rather than touching the
`Slot` table directly.

```
FUNCTION findFreeSlot():
    FOR each slot ORDERED BY slot_id:
        IF slot.status == FREE:
            RETURN slot.slot_id
    RETURN null   // lot is full

FUNCTION countFreeSlots():
    RETURN count of slots where status == FREE

FUNCTION countTotalSlots():
    RETURN count of all slots

FUNCTION occupySlot(slot_id):
    SET slot.status = OCCUPIED WHERE slot.slot_id = slot_id

FUNCTION freeSlot(slot_id):
    SET slot.status = FREE WHERE slot.slot_id = slot_id

FUNCTION addSlots(number_to_add):
    // Admin capability: grow capacity without disturbing existing slots
    start_id = MAX(existing slot_id) + 1
    FOR i = start_id TO start_id + number_to_add - 1:
        INSERT slot(id=i, status=FREE)
    RETURN new total slot count
```

## 2. Vehicle Entry Module

Handles a vehicle's arrival: rejects duplicates, rejects entry when full,
otherwise assigns a slot and opens a parking session.

```
FUNCTION isCurrentlyParked(plate):
    RETURN EXISTS a ParkingSession WHERE plate = plate AND status = ACTIVE

FUNCTION registerEntry(full_name, phone_number, vehicle_type, plate):
    plate = normalize(plate)   // uppercase, strip all whitespace

    IF isCurrentlyParked(plate):
        RETURN "Vehicle already registered and currently parked"

    slot_id = findFreeSlot()
    IF slot_id == null:
        RETURN "No slots available. Please try another parking facility."

    saveOrUpdateVehicle(plate, full_name, phone_number, vehicle_type)
    occupySlot(slot_id)

    INSERT ParkingSession(plate, slot_id, entry_time = now(), status = ACTIVE)

    RETURN "Vehicle registered at slot " + slot_id
```

**Note on scope:** an earlier design included a waiting queue for when the
lot is full. This was deliberately removed — if the lot is full, entry is
simply declined, matching the current brief.

## 3. Fee Calculation Module

Computes how long a vehicle has been parked and matches that duration
against the fee brackets stored in the `FeeTier` table.

```
FUNCTION calculateFee(plate):
    session = getActiveSession(plate)
    IF session == null:
        RETURN "Vehicle not found in parking."

    duration_minutes = (now() - session.entry_time) in minutes

    tiers = FeeTier ORDERED BY max_minutes ASCENDING
    FOR each tier in tiers:
        IF duration_minutes <= tier.max_minutes:
            RETURN duration_minutes, tier.fee

    RETURN duration_minutes, tiers.last.fee   // safety net
```

Fee tiers are read from the database rather than hardcoded, so management
can change prices (via **Admin → Edit rates**) without any code change.

## 4. Payment & Exit Module

Validates payment, records which method was used, and only then frees the
slot and opens the barrier.

```
VALID_METHODS = { mpesa, card, cash }

FUNCTION processExit(plate, amount_paid, payment_method):
    IF payment_method NOT IN VALID_METHODS:
        RETURN "Select a valid payment method"

    session = getActiveSession(plate)
    IF session == null:
        RETURN "Vehicle not found in parking. Exit denied."

    duration_minutes, fee = calculateFee(plate)

    IF amount_paid < fee:
        RETURN "Insufficient payment. Amount due: Kshs. " + fee

    openBarrier()

    UPDATE session SET exit_time = now(), fee_charged = fee,
                        payment_method = payment_method, status = COMPLETED

    freeSlot(session.slot_id)

    RETURN "Exit approved. Time: " + duration_minutes + " min, Paid: Kshs. " + fee
```

`payment_method` (M-Pesa / Card / Cash) is selected by the driver and
confirmed via a simulated confirmation step before this function runs —
no live payment gateway is connected (see README for details).

## 5. Display Module

A thin, read-only view over Slot Management — it owns no data of its own.
This is what feeds the driver-facing "visual display of parking slots"
required by the client brief.

```
FUNCTION getAvailabilityView():
    RETURN {
        free: countFreeSlots(),
        total: countTotalSlots(),
        slots: list of every slot with its status
    }
```

## 6. Reporting/Admin Module

Optional module (not in the original client requirements) added for
operational oversight: capacity management, revenue tracking, live
occupancy, history, and rate editing.

```
FUNCTION getActiveSessions():
    RETURN every ParkingSession WHERE status = ACTIVE, joined with Vehicle

FUNCTION getSessionHistory(limit):
    RETURN most recent ParkingSession WHERE status = COMPLETED, newest first

FUNCTION getTotalRevenue():
    RETURN SUM(fee_charged) WHERE status = COMPLETED

FUNCTION updateFeeTiers(tier_updates):
    VALIDATE each tier's max_minutes is strictly greater than the previous
    VALIDATE no fee is negative
    IF valid: UPDATE FeeTier rows accordingly
    RETURN success or a validation error message
```
