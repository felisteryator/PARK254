# Task One — Part (b): Data Structures and Reasons for Their Use

Park254 is implemented as a web application backed by SQLite, so the data
structures chosen at design time (part a) are realized as **database tables**
rather than in-memory structures. Each table was chosen to match how its
data is actually accessed in the algorithms.

## Slot table → Array-like, indexed by slot_id

**Structure:** a fixed set of rows, one per physical slot, with a primary
key on `slot_id`.

**Why:** the number of slots is known and bounded (a real parking lot), and
`slot_id` is a small sequential integer — exactly the access pattern an
array is built for. `findFreeSlot()` scans slots in `slot_id` order, and a
lookup or update by `slot_id` is a direct, indexed access rather than a
search. Growing capacity (`addSlots()`) simply appends new rows after the
current highest `slot_id`, the same way an array would grow.

## Vehicle table → Hash-map-like, keyed by plate

**Structure:** one row per vehicle, with `plate` as the primary key.

**Why:** every operation on this table — the duplicate check in
`registerEntry()`, looking up a driver's details, updating contact info on
a repeat visit — is a lookup **by plate**, never a scan. Making `plate` the
primary key gives SQLite an index on it automatically, so a lookup is
effectively O(1)/O(log n) rather than O(n). This is the same justification
that led to choosing a hash map at the algorithm-design stage; the SQL
primary key is how that choice is physically realized.

## ParkingSession table → Records indexed by plate and by status

**Structure:** one row per visit (a vehicle can have many rows over time),
with `plate` and `slot_id` as foreign keys and a `status` column
(`ACTIVE` / `COMPLETED`).

**Why:** this table plays two roles at once — it's both the `active_records`
structure from the algorithm design (rows with `status = ACTIVE`, queried
by plate) and the permanent historical log (`status = COMPLETED`, queried
by `exit_time` for the History page). Splitting a vehicle's *identity*
(`Vehicle`) from its *visits* (`ParkingSession`) avoids re-entering a
driver's details every time the same plate returns, and lets the system
answer "is this plate currently parked?" with a single indexed lookup
rather than scanning a full history.

## FeeTier table → Ordered lookup table (array of brackets)

**Structure:** a small, ordered set of rows, each with a `max_minutes`
upper bound and a `fee`.

**Why:** the pricing rule is a small number of fixed brackets checked in
order — exactly what an ordered array/lookup table is for.
`calculateFee()` walks the tiers in ascending `max_minutes` order and
returns the first one a duration fits under. Storing this as data (not
hardcoded `if/else` logic in Python) is what makes **Admin → Edit rates**
possible: changing a price is a row update, not a code change.

## Design note: no queue

An earlier design iteration included a waiting-queue structure (FIFO) for
when the lot is full. This was deliberately removed from the current
implementation — the brief does not require it, and entry is simply
declined when no slot is free. If reinstated, a `WaitingQueueEntry` table
ordered by `joined_at` would serve the same purpose a FIFO queue does at
the algorithm level: `ORDER BY joined_at ASC` gives the same ordering
guarantee a queue's enqueue/dequeue operations would.

## Summary table

| Data | Structure | Physical realization | Key reason |
|---|---|---|---|
| Slots | Array-like, indexed by slot_id | `Slot` table, PK on `slot_id` | Fixed size, sequential, direct access |
| Vehicles | Hash map, keyed by plate | `Vehicle` table, PK on `plate` | All access is lookup-by-plate |
| Parking sessions | Indexed records (active + historical) | `ParkingSession` table, FK to Vehicle/Slot | Dual role: live state + audit log |
| Fee tiers | Ordered lookup table | `FeeTier` table | Small, ordered, data-driven pricing |
