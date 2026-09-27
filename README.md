# Park254 — Modern Parking System

A web-based parking management system that displays available parking slots in real time, helping drivers know the parking status before arriving and reducing congestion.

## Features

- **Live slot display** — drivers see real-time slot availability before
  entering (green = free, red = occupied, with a text label either way)
- **Vehicle entry** — captures driver name, phone, vehicle type, and plate;
  rejects duplicates and rejects entry when the lot is full
- **Automatic fee calculation** — duration and amount due are computed
  automatically from tiered pricing brackets, viewable before paying via
  "Check amount due"
- **Payment at exit** — driver selects M-Pesa, Card, or Cash, confirms via
  a simulated confirmation step, and the barrier only "opens" once payment
  is confirmed
- **Admin dashboard** (password-protected) — live occupancy, total
  revenue, currently-parked vehicles, capacity management, and editable
  parking rates
- **Session history** — a permanent, auditable log of every completed
  visit, including which payment method was used

## Tech stack

- **Python 3 + Flask** — web server and routing
- **SQLite** — database (no separate server needed)
- **Jinja2 + vanilla JavaScript** — templates and interactivity, no
  frontend framework

## Project structure

```
park254/
├── app.py                  # Flask routes — the web layer
├── database.py              # Schema creation and migrations
├── modules/                  # Business logic, one file per module
│   ├── slot_management.py
│   ├── vehicle_entry.py
│   ├── fee_calculation.py
│   ├── payment_exit.py
│   ├── display.py
│   └── reporting.py
├── templates/                 # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html               # Slot availability (homepage)
│   ├── entry.html                 # Vehicle entry form
│   ├── exit.html                    # Vehicle exit / payment form
│   ├── admin.html                     # Admin dashboard
│   ├── admin_login.html                 # Admin password gate
│   ├── admin_rates.html                   # Edit parking rates
│   └── history.html                         # Completed session history
├── docs/                        # Task One documentation (this folder)
│   ├── 01_algorithms.md
│   ├── 02_data_structures.md
│   ├── 03_database_design.md
│   └── erd.png
└── parking.db                     # SQLite database (created on first run)
```

## Running it locally

1. Install Flask:
   ```
   pip install flask
   ```
2. Run the app:
   ```
   python app.py
   ```
3. Open the URL printed in the terminal (typically
   `http://127.0.0.1:5000`) in a browser.

The database and its tables are created automatically on first run — no
manual setup required.

## Admin access

Visit **Admin** in the navigation bar. Default password:

```
park254admin
```

Change this in `app.py` (the `ADMIN_PASSWORD` constant) before any real
deployment.

## Documentation

The `docs/` folder contains the Task One deliverables this system is
built from:

- **`01_algorithms.md`** — pseudocode for every module (part a)
- **`02_data_structures.md`** — data structures used and why (part b)
- **`03_database_design.md`** — full schema, relationships, and the ERD
  (part c)

## Known limitations (honest disclosure)

- **Payment is simulated, not live.** M-Pesa and Card payments show a
  realistic confirmation step, but there is no real Safaricom Daraja API
  or card payment gateway connected — that would require live merchant
  credentials outside the scope of this coursework build.
- **The barrier is simulated.** `open_barrier()` logs to the server
  console rather than signalling real hardware.
- **The admin password is a single shared secret**, stored in plaintext in
  `app.py` — adequate for demonstrating access control, not for a
  production deployment.
- 
