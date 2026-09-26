"""
Park254 - Flask Web Application
Routes are the "web-based system" layer required by Task Two.
Each route calls straight into the module functions built in Task One's
module breakdown — this file doesn't contain any business logic itself.
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from functools import wraps
from database import init_db
from modules import display, vehicle_entry, payment_exit, reporting, slot_management, fee_calculation

app = Flask(__name__)
app.secret_key = "park254-dev-secret-change-this-in-production"  # needed for session cookies to work

ADMIN_PASSWORD = "park254admin"  # simple shared password — fine for coursework, not for real deployment


def login_required(view_func):
    """Redirects to the admin login page unless the session is already authenticated."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    """
    Driver-facing homepage — the 'visual display of parking slots
    available before entry' required by the client brief.
    """
    view = display.get_availability_view()
    return render_template("index.html", view=view)


@app.route("/entry", methods=["GET", "POST"])
def entry():
    """
    GET: show the entry form.
    POST: register the vehicle via the Vehicle Entry Module.
    """
    result = None
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        vehicle_type = request.form.get("vehicle_type", "").strip()
        plate = request.form.get("plate", "").strip()

        result = vehicle_entry.register_entry(full_name, phone_number, vehicle_type, plate)

    return render_template("entry.html", result=result)


@app.route("/exit", methods=["GET", "POST"])
def exit_page():
    """
    GET: show the exit form.
    POST: process payment and exit via the Payment & Exit Module.
    """
    result = None
    if request.method == "POST":
        plate = request.form.get("plate", "").strip()
        amount_str = request.form.get("amount_paid", "0").strip()
        payment_method = request.form.get("payment_method", "").strip()
        try:
            amount_paid = float(amount_str)
        except ValueError:
            amount_paid = -1  # forces "insufficient payment" rather than crashing on bad input

        result = payment_exit.process_exit(plate, amount_paid, payment_method)

    return render_template("exit.html", result=result)

@app.route("/exit/check")
def exit_check():
    """
    JSON lookup used by the exit page's 'Check amount due' button.
    Lets the driver see the exact fee, entry time, and elapsed duration
    before they type an amount and submit payment.
    """
    plate = request.args.get("plate", "").strip()
    if not plate:
        return jsonify({"success": False, "message": "Enter a plate number first."})

    normalized_plate = plate.strip().upper().replace(" ", "")
    active_session = fee_calculation.get_active_session(normalized_plate)
    if active_session is None:
        return jsonify({"success": False, "message": "Vehicle not found in parking."})

    fee_result = fee_calculation.calculate_fee(normalized_plate)
    return jsonify({
        "success": True,
        "entry_time": active_session["entry_time"],
        "duration_minutes": fee_result["duration_minutes"],
        "fee": fee_result["fee"]
    })


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """
    GET: show current capacity and the add-slots form.
    POST: expand capacity via the Reporting/Admin Module.
    """
    result = None
    if request.method == "POST":
        try:
            number_to_add = int(request.form.get("number_to_add", "0"))
        except ValueError:
            number_to_add = 0
        result = reporting.expand_capacity(number_to_add)

    current_total = slot_management.count_total_slots()
    current_free = slot_management.count_free_slots()
    revenue = reporting.get_total_revenue()
    active_sessions = reporting.get_active_sessions()
    return render_template("admin.html", result=result, current_total=current_total,
                            current_free=current_free, revenue=revenue, active_sessions=active_sessions)


@app.route("/admin/rates", methods=["GET", "POST"])
@login_required
def admin_rates():
    """
    GET: show the current fee tiers as an editable form.
    POST: validate and save the new rates via the Reporting/Admin Module.
    """
    result = None
    if request.method == "POST":
        tiers = reporting.get_fee_tiers()  # need tier_ids to know which rows to update
        tier_updates = []
        for tier in tiers:
            tid = tier["tier_id"]
            try:
                max_minutes = int(request.form.get(f"max_minutes_{tid}", ""))
                fee = float(request.form.get(f"fee_{tid}", ""))
            except ValueError:
                result = {"success": False, "message": "All fields must be valid numbers."}
                break
            tier_updates.append({"tier_id": tid, "max_minutes": max_minutes, "fee": fee})
        else:
            result = reporting.update_fee_tiers(tier_updates)

    tiers = reporting.get_fee_tiers()
    return render_template("admin_rates.html", tiers=tiers, result=result)


@app.route("/history")
@login_required
def history():
    """Shows the most recent completed parking sessions."""
    sessions = reporting.get_session_history(limit=50)
    return render_template("history.html", sessions=sessions)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Simple shared-password gate in front of the admin area."""
    error = None
    if request.method == "POST":
        entered_password = request.form.get("password", "")
        if entered_password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin"))
        error = "Incorrect password."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    init_db()  # ensures tables exist and slots are seeded before the server starts
    app.run(debug=True, port=5000)