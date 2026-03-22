from datetime import date

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, redirect, render_template, request, session, url_for, flash

from config import get_db
from kseb import kseb_calculate_bill, KSEB_RULES


app = Flask(__name__)
app.secret_key = __import__("os").environ.get("SECRET_KEY", "change-this-secret-in-production")


def ensure_seed_data():
    """Seed Supabase tables with sensible defaults if empty."""
    sb = get_db()
    try:
        r = sb.table("admins").select("id").limit(1).execute()
        if not r.data:
            sb.table("admins").insert({"username": "admin", "password": "admin123"}).execute()
    except Exception:
        pass
    try:
        r = sb.table("appliances").select("id").limit(1).execute()
        if not r.data:
            appliances = [
                {"appliance_name": "LED Bulb 9W", "power_rating_watts": 9},
                {"appliance_name": "LED Tube Light 20W", "power_rating_watts": 20},
                {"appliance_name": "Ceiling Fan", "power_rating_watts": 60},
                {"appliance_name": "Refrigerator 190L", "power_rating_watts": 180},
                {"appliance_name": "Refrigerator 300L", "power_rating_watts": 250},
                {"appliance_name": "1 Ton Inverter AC", "power_rating_watts": 1200},
                {"appliance_name": "1.5 Ton Inverter AC", "power_rating_watts": 1500},
                {"appliance_name": "Washing Machine (Front Load)", "power_rating_watts": 500},
                {"appliance_name": 'LED TV 32"', "power_rating_watts": 60},
                {"appliance_name": 'LED TV 43"', "power_rating_watts": 90},
                {"appliance_name": "Laptop Charger", "power_rating_watts": 65},
                {"appliance_name": "Desktop PC", "power_rating_watts": 200},
                {"appliance_name": "Water Heater (Geyser)", "power_rating_watts": 2000},
                {"appliance_name": "Mixer Grinder", "power_rating_watts": 750},
                {"appliance_name": "Electric Iron", "power_rating_watts": 1000},
            ]
            sb.table("appliances").insert(appliances).execute()
    except Exception:
        pass
    try:
        r = sb.table("tariffs").select("id").limit(1).execute()
        if not r.data:
            sb.table("tariffs").insert({"rate_per_kwh": 8.0, "effective_date": date.today().isoformat()}).execute()
    except Exception:
        pass


def get_current_tariff():
    sb = get_db()
    r = sb.table("tariffs").select("rate_per_kwh").order("effective_date", desc=True).limit(1).execute()
    return r.data[0]["rate_per_kwh"] if r.data else 0


@app.route("/health")
def health():
    """Check if Supabase is configured and reachable."""
    try:
        db = get_db()
        db.table("admins").select("id").limit(1).execute()
        return "OK"
    except RuntimeError as e:
        return str(e), 503
    except Exception as e:
        return str(e), 503


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("user_dashboard"))
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            sb = get_db()
            r = sb.table("users").select("id").eq("email", email).execute()
            if r.data:
                flash("This email is already registered. Please log in instead.")
                return redirect(url_for("login"))
            sb.table("users").insert({"name": name, "email": email, "password": password}).execute()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except RuntimeError as e:
            app.logger.error("Config error: %s", e)
            return "Server misconfigured: missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. Check Render Environment.", 500
        except Exception as e:
            app.logger.exception("Register failed: %s", e)
            msg = str(e) if "relation" in str(e).lower() or "supabase" in str(e).lower() else "Registration failed."
            return msg, 500
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            sb = get_db()
            r = sb.table("admins").select("*").eq("username", username).execute()
            if r.data and r.data[0].get("password") == password:
                session.clear()
                session["admin_id"] = str(r.data[0]["id"])
                return redirect(url_for("admin_dashboard"))
            r = sb.table("users").select("*").eq("email", username).execute()
            if r.data and r.data[0].get("password") == password:
                session.clear()
                session["user_id"] = str(r.data[0]["id"])
                session["user_name"] = r.data[0].get("name", "")
                return redirect(url_for("platform"))
            flash("Invalid credentials.")
        except RuntimeError as e:
            app.logger.error("Config error: %s", e)
            return "Server misconfigured: missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY.", 500
        except Exception as e:
            app.logger.exception("Login failed: %s", e)
            err = str(e)
            if "SUPABASE" in err.upper() or "relation" in err.lower():
                return err, 500
            return "Login failed. Check server logs.", 500
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/platform")
def platform():
    if "user_id" not in session:
        return redirect(url_for("login"))
    try:
        return _render_platform(session["user_id"])
    except Exception as e:
        app.logger.exception("Platform failed: %s", e)
        return f"Error loading platform: {str(e)}", 500


@app.route("/map/kerala-power")
def kerala_power_map():
    """Live map of Kerala power infrastructure (poles, towers, lines) from OpenStreetMap."""
    user_id = session.get("user_id")
    admin_id = session.get("admin_id")
    return render_template("kerala_power_map.html", user_id=user_id, admin_id=admin_id)


def _render_platform(user_id):
    sb = get_db()
    r = sb.table("appliances").select("*").execute()
    appliance_docs = r.data or []
    appliances = [
        {"appliance_id": str(a["id"]), "appliance_name": a["appliance_name"], "power_rating_watts": a["power_rating_watts"]}
        for a in appliance_docs
    ]
    appliance_map = {str(a["id"]): a for a in appliance_docs}

    r = sb.table("usage").select("*").eq("user_id", user_id).execute()
    usage_docs = r.data or []
    tariff = get_current_tariff()
    usage_records = []
    appliance_cost_breakdown = []
    for u in usage_docs:
        app_doc = appliance_map.get(str(u["appliance_id"]))
        if app_doc:
            kwh = (app_doc["power_rating_watts"] * u["hours_per_day"] * u["number_of_days"]) / 1000.0
            cost = round(kwh * tariff, 0)
            usage_records.append({
                "usage_id": str(u["id"]),
                "appliance_name": app_doc["appliance_name"],
                "power_rating_watts": app_doc["power_rating_watts"],
                "hours_per_day": u["hours_per_day"],
                "number_of_days": u["number_of_days"],
            })
            appliance_cost_breakdown.append({
                "appliance_name": app_doc["appliance_name"],
                "units_kwh": round(kwh, 1),
                "cost": cost,
            })

    r = sb.table("bills").select("*").eq("user_id", user_id).order("bill_date", desc=True).execute()
    bill_docs = r.data or []
    bills = [
        {"bill_id": str(b["id"]), "bill_date": b.get("bill_date", ""), "total_units": b.get("total_units", 0), "total_cost": b.get("total_cost", 0)}
        for b in bill_docs
    ]

    r = sb.table("facilities").select("*").eq("user_id", user_id).execute()
    facilities = r.data or []

    total_kwh = 0.0
    for u in usage_docs:
        app_doc = appliance_map.get(str(u["appliance_id"]))
        if app_doc:
            total_kwh += (app_doc["power_rating_watts"] * u["hours_per_day"] * u["number_of_days"]) / 1000.0
    tariff = get_current_tariff()
    current_month_cost = round(total_kwh * tariff, 0)

    r = sb.table("users").select("monthly_budget").eq("id", user_id).execute()
    user_budget = (r.data[0].get("monthly_budget") or 0) if r.data else 0

    alerts = []
    if user_budget and current_month_cost > user_budget:
        alerts.append({"type": "high", "message": "⚠ Budget exceeded. Current est. cost ₹" + str(int(current_month_cost)) + " vs budget ₹" + str(user_budget) + "."})
    elif total_kwh > 200:
        alerts.append({"type": "high", "message": "⚠ High usage detected (" + str(round(total_kwh, 0)) + " kWh this period). Consider reducing AC/heating hours."})

    # High-usage appliance alerts
    for item in appliance_cost_breakdown:
        if item["units_kwh"] >= 80:
            alerts.append({"type": "high", "message": "⚠ " + item["appliance_name"] + " consumed " + str(item["units_kwh"]) + " kWh. Reduce usage or adjust settings."})

    # Energy efficiency recommendations
    recommendations = [
        "Replace incandescent bulbs with LED bulbs.",
        "Set AC to 24°C and limit hours during peak times.",
        "Turn off appliances completely instead of standby mode.",
    ]
    if any("AC" in a["appliance_name"] for a in appliance_cost_breakdown):
        recommendations.insert(1, "Consider upgrading to Inverter AC for ~30% savings.")
    if total_kwh > 150:
        recommendations.append("Use geyser only when needed; switch off after use.")

    return render_template(
        "platform.html",
        user_name=session.get("user_name", ""),
        current_tariff=get_current_tariff(),
        kseb_rules=KSEB_RULES,
        appliances=appliances,
        usage_records=usage_records,
        bills=bills,
        facilities=facilities,
        current_month_kwh=round(total_kwh, 1),
        current_month_cost=int(current_month_cost),
        user_budget=user_budget,
        remaining_budget=int(user_budget - current_month_cost) if user_budget else 0,
        alerts=alerts,
        appliance_cost_breakdown=appliance_cost_breakdown,
        recommendations=recommendations,
        carbon_kg=round(total_kwh * 0.8, 1),
    )


@app.route("/user/add_facility", methods=["POST"])
def add_facility():
    if "user_id" not in session:
        return redirect(url_for("login"))
    sb = get_db()
    sb.table("facilities").insert({
        "user_id": session["user_id"],
        "name": request.form.get("name", ""),
        "type": request.form.get("type", "Building"),
        "zone": request.form.get("zone", ""),
    }).execute()
    flash("Facility added.")
    return redirect(url_for("platform"))


@app.route("/user/set_budget", methods=["POST"])
def set_budget():
    if "user_id" not in session:
        return redirect(url_for("login"))
    budget = float(request.form.get("budget", 0) or 0)
    sb = get_db()
    sb.table("users").update({"monthly_budget": budget}).eq("id", session["user_id"]).execute()
    flash("Budget saved.")
    return redirect(url_for("platform"))


@app.route("/api/geocode")
def api_geocode():
    """Search for places (Nominatim) - restricts to Kerala bounding box."""
    import json
    import urllib.request
    import urllib.parse
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])
    try:
        # Kerala bbox: south, west, north, east
        viewbox = "74.9,8.2,77.3,12.8"
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
            "q": q + ", Kerala India",
            "format": "json",
            "limit": 8,
            "viewbox": viewbox,
            "bounded": 1,
        })
        req = urllib.request.Request(url, headers={"User-Agent": "SmartEnergyPlatform/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return jsonify([{"lat": float(r["lat"]), "lng": float(r["lon"]), "display_name": r.get("display_name", "")} for r in data])
    except Exception as e:
        app.logger.warning("Geocode: %s", e)
        return jsonify([])


OVERPASS_SERVERS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]


@app.route("/api/overpass")
def api_overpass():
    """Proxy Overpass API to avoid CORS. Query in 'q' param. Tries multiple servers."""
    import json
    import urllib.request
    import urllib.parse
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "Missing query"}), 400
    body = ("data=" + urllib.parse.quote(q)).encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "SmartEnergyPlatform/1.0"}
    last_err = None
    for url in OVERPASS_SERVERS:
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
                return jsonify(data)
        except Exception as e:
            last_err = e
            continue
    return jsonify({"error": str(last_err), "elements": []}), 502


@app.route("/api/map/power-reports")
def api_power_reports():
    """Return all power reports (no current, admin markers) for the Kerala map."""
    try:
        sb = get_db()
        r = sb.table("power_reports").select("*").execute()
        reports = []
        for row in (r.data or []):
            reports.append({
                "id": str(row["id"]),
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
                "report_type": row.get("report_type", "no_current"),
                "description": row.get("description", ""),
                "status": row.get("status", "pending"),
                "reporter_type": row.get("reporter_type", "user"),
                "created_at": row.get("created_at", ""),
            })
        return jsonify(reports)
    except Exception as e:
        if "relation" in str(e).lower() or "does not exist" in str(e).lower():
            return jsonify([])
        return jsonify({"error": str(e)}), 500


@app.route("/map/report", methods=["POST"])
def map_report():
    """User reports 'no current' or other power issue at a map location."""
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    data = request.json if request.is_json else None
    lat = request.form.get("lat") or (data.get("lat") if data else None)
    lng = request.form.get("lng") or (data.get("lng") if data else None)
    report_type = request.form.get("report_type") or (data.get("report_type") if data else None) or "no_current"
    description = request.form.get("description") or (data.get("description") if data else "") or ""
    if lat is None or lng is None:
        return jsonify({"error": "Location (lat, lng) required"}), 400
    try:
        lat, lng = float(lat), float(lng)
        sb = get_db()
        sb.table("power_reports").insert({
            "lat": lat, "lng": lng, "report_type": report_type, "description": description,
            "reporter_type": "user", "user_id": session["user_id"], "status": "pending"
        }).execute()
        if request.is_json or request.headers.get("Accept") == "application/json":
            return jsonify({"ok": True, "message": "Report submitted. It will appear on the map for inspection."})
        flash("Report submitted. It will appear on the map for inspection.")
        return redirect(url_for("kerala_power_map"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/map/marker", methods=["POST"])
def admin_map_marker():
    """Admin adds infrastructure marker (ok, issue, maintenance) on the map."""
    wants_json = "application/json" in request.accept_mimetypes
    if "admin_id" not in session:
        if wants_json:
            return jsonify({"error": "Login required"}), 401
        return redirect(url_for("login"))
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    report_type = request.form.get("report_type", "issue")
    description = request.form.get("description", "")
    if not lat or not lng:
        if wants_json:
            return jsonify({"error": "Location required"}), 400
        flash("Location (lat, lng) required.")
        return redirect(request.referrer or url_for("admin_dashboard"))
    try:
        sb = get_db()
        sb.table("power_reports").insert({
            "lat": float(lat), "lng": float(lng), "report_type": report_type, "description": description,
            "reporter_type": "admin", "admin_id": session["admin_id"], "status": "pending"
        }).execute()
        if wants_json:
            return jsonify({"ok": True})
        flash("Marker added to map.")
    except Exception as e:
        if wants_json:
            return jsonify({"error": str(e)}), 500
        flash(f"Failed: {str(e)}")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/map/reports")
def admin_map_reports():
    """Analyst dashboard: power reports with stats, breakdowns, filters, export."""
    if "admin_id" not in session:
        return redirect(url_for("login"))
    status_filter = request.args.get("status", "")
    type_filter = request.args.get("type", "")
    try:
        sb = get_db()
        r = sb.table("power_reports").select("*").order("created_at", desc=True).execute()
        rows = r.data or []
        reports = []
        for row in rows:
            rep = {
                "id": str(row["id"]),
                "lat": row["lat"],
                "lng": row["lng"],
                "report_type": row.get("report_type", ""),
                "description": row.get("description", ""),
                "status": row.get("status", "pending"),
                "reporter_type": row.get("reporter_type", ""),
                "created_at": str(row.get("created_at", ""))[:19] if row.get("created_at") else "",
            }
            if status_filter and rep["status"] != status_filter:
                continue
            if type_filter and rep["report_type"] != type_filter:
                continue
            reports.append(rep)

        # Analyst stats
        by_status = {}
        by_type = {}
        for row in rows:
            s = row.get("status", "pending")
            by_status[s] = by_status.get(s, 0) + 1
            t = row.get("report_type", "no_current")
            by_type[t] = by_type.get(t, 0) + 1

        stats = {
            "total": len(rows),
            "pending": by_status.get("pending", 0),
            "inspected": by_status.get("inspected", 0),
            "resolved": by_status.get("resolved", 0),
            "by_type": by_type,
            "by_status": by_status,
        }
        return render_template("admin_map_reports.html", reports=reports, stats=stats, error=None)
    except Exception as e:
        return render_template("admin_map_reports.html", reports=[], stats={}, error=str(e))


@app.route("/admin/map/reports/export")
def admin_map_reports_export():
    """Export power reports as CSV for analysts."""
    if "admin_id" not in session:
        return redirect(url_for("login"))
    try:
        sb = get_db()
        r = sb.table("power_reports").select("*").order("created_at", desc=True).execute()
        rows = r.data or []
    except Exception:
        rows = []
    import csv
    import io
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["id", "lat", "lng", "report_type", "description", "status", "reporter_type", "created_at"])
    for row in rows:
        w.writerow([
            str(row.get("id", "")),
            row.get("lat", ""),
            row.get("lng", ""),
            row.get("report_type", ""),
            row.get("description", ""),
            row.get("status", ""),
            row.get("reporter_type", ""),
            str(row.get("created_at", ""))[:19] if row.get("created_at") else "",
        ])
    from flask import Response
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=power_reports.csv"})


@app.route("/admin/map/report/<id>/status", methods=["POST"])
def admin_report_status(id):
    """Admin marks report as inspected or resolved."""
    if "admin_id" not in session:
        return redirect(url_for("login"))
    status = request.form.get("status", "inspected")
    if status not in ("inspected", "resolved"):
        status = "inspected"
    try:
        sb = get_db()
        sb.table("power_reports").update({"status": status}).eq("id", id).execute()
        flash(f"Report marked as {status}.")
    except Exception as e:
        flash(f"Failed: {str(e)}")
    return redirect(request.referrer or url_for("admin_map_reports"))


@app.route("/api/kseb/estimate")
def api_kseb_estimate():
    """Return KSEB bill estimate for given units (query param: units)."""
    units = float(request.args.get("units", 0) or 0)
    bill = kseb_calculate_bill(units)
    return jsonify(bill)


@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    sb = get_db()

    r = sb.table("appliances").select("*").execute()
    appliance_docs = r.data or []
    appliances = [
        {"appliance_id": str(a["id"]), "appliance_name": a["appliance_name"], "power_rating_watts": a["power_rating_watts"]}
        for a in appliance_docs
    ]
    appliance_map = {str(a["id"]): a for a in appliance_docs}

    r = sb.table("usage").select("*").eq("user_id", user_id).execute()
    usage_docs = r.data or []
    usage_records = []
    for u in usage_docs:
        app_doc = appliance_map.get(str(u["appliance_id"]))
        if not app_doc:
            continue
        usage_records.append({
            "usage_id": str(u["id"]),
            "appliance_name": app_doc["appliance_name"],
            "power_rating_watts": app_doc["power_rating_watts"],
            "hours_per_day": u["hours_per_day"],
            "number_of_days": u["number_of_days"],
        })

    r = sb.table("bills").select("*").eq("user_id", user_id).order("bill_date", desc=True).execute()
    bill_docs = r.data or []
    bills = [
        {"bill_id": str(b["id"]), "bill_date": b.get("bill_date", ""), "total_units": b.get("total_units", 0), "total_cost": b.get("total_cost", 0)}
        for b in bill_docs
    ]
    return render_template(
        "user_dashboard.html",
        user_name=session.get("user_name", ""),
        appliances=appliances,
        usage_records=usage_records,
        bills=bills,
        current_tariff=get_current_tariff(),
    )


@app.route("/user/add_usage", methods=["POST"])
def add_usage():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    appliance_id = request.form.get("appliance_id")
    hours_per_day = int(request.form.get("hours_per_day", 0))
    number_of_days = int(request.form.get("number_of_days", 0))

    sb = get_db()
    sb.table("usage").insert({
        "user_id": user_id,
        "appliance_id": appliance_id,
        "hours_per_day": hours_per_day,
        "number_of_days": number_of_days,
    }).execute()

    r = sb.table("appliances").select("*").execute()
    appliance_docs = r.data or []
    appliance_map = {str(a["id"]): a for a in appliance_docs}

    r = sb.table("usage").select("*").eq("user_id", user_id).execute()
    usage_docs = r.data or []
    total_kwh = 0.0
    for u in usage_docs:
        app_doc = appliance_map.get(str(u["appliance_id"]))
        if not app_doc:
            continue
        power_watts = app_doc["power_rating_watts"]
        hrs = u["hours_per_day"]
        days = u["number_of_days"]
        total_kwh += (power_watts * hrs * days) / 1000.0

    tariff = get_current_tariff()
    total_cost = total_kwh * tariff
    today = date.today().isoformat()

    sb.table("bills").insert({
        "user_id": user_id,
        "total_units": total_kwh,
        "total_cost": total_cost,
        "bill_date": today,
    }).execute()
    flash("Usage added and bill recomputed.")
    return redirect(url_for("user_dashboard"))


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("login"))

    sb = get_db()

    r = sb.table("appliances").select("*").execute()
    appliance_docs = r.data or []
    appliances = [
        {"appliance_id": str(a["id"]), "appliance_name": a["appliance_name"], "power_rating_watts": a["power_rating_watts"]}
        for a in appliance_docs
    ]

    r = sb.table("tariffs").select("*").order("effective_date", desc=True).execute()
    tariff_docs = r.data or []
    tariffs = [
        {"tariff_id": str(t["id"]), "rate_per_kwh": t["rate_per_kwh"], "effective_date": t["effective_date"]}
        for t in tariff_docs
    ]

    r = sb.table("bills").select("*").order("bill_date", desc=True).execute()
    bill_docs = r.data or []
    user_ids = list({str(b["user_id"]) for b in bill_docs})
    user_map = {}
    if user_ids:
        r = sb.table("users").select("id, name").in_("id", user_ids).execute()
        user_map = {str(u["id"]): u.get("name", "") for u in (r.data or [])}

    bills = [
        {"bill_id": str(b["id"]), "name": user_map.get(str(b["user_id"]), ""), "bill_date": b.get("bill_date", ""), "total_units": b.get("total_units", 0), "total_cost": b.get("total_cost", 0)}
        for b in bill_docs
    ]
    return render_template(
        "admin_dashboard.html",
        appliances=appliances,
        tariffs=tariffs,
        bills=bills,
    )


@app.route("/admin/appliance", methods=["POST"])
def admin_add_appliance():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    name = request.form.get("appliance_name")
    power = int(request.form.get("power_rating_watts", 0))
    sb = get_db()
    sb.table("appliances").insert({"appliance_name": name, "power_rating_watts": power}).execute()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/tariff", methods=["POST"])
def admin_add_tariff():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    rate = float(request.form.get("rate_per_kwh", 0))
    effective = request.form.get("effective_date")
    sb = get_db()
    sb.table("tariffs").insert({"rate_per_kwh": rate, "effective_date": effective}).execute()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/appliance/<id>/delete", methods=["POST"])
def admin_delete_appliance(id):
    if "admin_id" not in session:
        return redirect(url_for("login"))
    try:
        sb = get_db()
        sb.table("appliances").delete().eq("id", id).execute()
        flash("Appliance deleted.")
    except Exception as e:
        if "foreign key" in str(e).lower() or "violates" in str(e).lower():
            flash("Cannot delete: appliance is in use. Remove usage records first.")
        else:
            flash(f"Delete failed: {str(e)}")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/tariff/<id>/delete", methods=["POST"])
def admin_delete_tariff(id):
    if "admin_id" not in session:
        return redirect(url_for("login"))
    try:
        sb = get_db()
        sb.table("tariffs").delete().eq("id", id).execute()
        flash("Tariff deleted.")
    except Exception as e:
        flash(f"Delete failed: {str(e)}")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/bill/<id>/delete", methods=["POST"])
def admin_delete_bill(id):
    if "admin_id" not in session:
        return redirect(url_for("login"))
    try:
        sb = get_db()
        sb.table("bills").delete().eq("id", id).execute()
        flash("Bill deleted.")
    except Exception as e:
        flash(f"Delete failed: {str(e)}")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/appliance/<id>/edit", methods=["GET", "POST"])
def admin_edit_appliance(id):
    if "admin_id" not in session:
        return redirect(url_for("login"))
    sb = get_db()
    if request.method == "POST":
        name = request.form.get("appliance_name")
        power = int(request.form.get("power_rating_watts", 0))
        sb.table("appliances").update({"appliance_name": name, "power_rating_watts": power}).eq("id", id).execute()
        flash("Appliance updated.")
        return redirect(url_for("admin_dashboard"))
    r = sb.table("appliances").select("*").eq("id", id).execute()
    if not r.data:
        flash("Appliance not found.")
        return redirect(url_for("admin_dashboard"))
    a = r.data[0]
    return render_template("admin_edit_appliance.html", appliance=a)


@app.route("/admin/tariff/<id>/edit", methods=["GET", "POST"])
def admin_edit_tariff(id):
    if "admin_id" not in session:
        return redirect(url_for("login"))
    sb = get_db()
    if request.method == "POST":
        rate = float(request.form.get("rate_per_kwh", 0))
        effective = request.form.get("effective_date")
        sb.table("tariffs").update({"rate_per_kwh": rate, "effective_date": effective}).eq("id", id).execute()
        flash("Tariff updated.")
        return redirect(url_for("admin_dashboard"))
    r = sb.table("tariffs").select("*").eq("id", id).execute()
    if not r.data:
        flash("Tariff not found.")
        return redirect(url_for("admin_dashboard"))
    t = r.data[0]
    return render_template("admin_edit_tariff.html", tariff=t)


@app.route("/admin/data")
def admin_data():
    """Database overview: see all data and where it lives."""
    if "admin_id" not in session:
        return redirect(url_for("login"))
    sb = get_db()
    counts = {}
    try:
        for table in ["admins", "users", "appliances", "usage", "bills", "facilities", "tariffs", "power_reports"]:
            try:
                r = sb.table(table).select("*").execute()
                counts[table] = len(r.data or [])
            except Exception:
                counts[table] = 0
    except Exception as e:
        counts = {"error": str(e)}
    return render_template("admin_data.html", counts=counts)


@app.route("/user/usage/<id>/edit", methods=["GET", "POST"])
def user_edit_usage(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    sb = get_db()
    if request.method == "POST":
        hours = int(request.form.get("hours_per_day", 0))
        days = int(request.form.get("number_of_days", 0))
        sb.table("usage").update({"hours_per_day": hours, "number_of_days": days}).eq("id", id).eq("user_id", user_id).execute()
        flash("Usage updated.")
        return redirect(url_for("user_dashboard"))
    r = sb.table("usage").select("*").eq("id", id).eq("user_id", user_id).execute()
    if not r.data:
        flash("Usage record not found.")
        return redirect(url_for("user_dashboard"))
    u = r.data[0]
    r2 = sb.table("appliances").select("*").eq("id", u["appliance_id"]).execute()
    app = r2.data[0] if r2.data else {}
    return render_template("user_edit_usage.html", usage=u, appliance=app)


@app.route("/user/usage/<id>/delete", methods=["POST"])
def user_delete_usage(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    try:
        sb = get_db()
        sb.table("usage").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Usage record deleted.")
    except Exception as e:
        flash(f"Delete failed: {str(e)}")
    return redirect(url_for("user_dashboard"))


@app.route("/user/facility/<id>/edit", methods=["GET", "POST"])
def user_edit_facility(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    sb = get_db()
    if request.method == "POST":
        name = request.form.get("name", "")
        ftype = request.form.get("type", "Building")
        zone = request.form.get("zone", "")
        sb.table("facilities").update({"name": name, "type": ftype, "zone": zone}).eq("id", id).eq("user_id", user_id).execute()
        flash("Facility updated.")
        return redirect(url_for("platform"))
    r = sb.table("facilities").select("*").eq("id", id).eq("user_id", user_id).execute()
    if not r.data:
        flash("Facility not found.")
        return redirect(url_for("platform"))
    f = r.data[0]
    return render_template("user_edit_facility.html", facility=f)


@app.route("/user/facility/<id>/delete", methods=["POST"])
def user_delete_facility(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    try:
        sb = get_db()
        sb.table("facilities").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Facility deleted.")
    except Exception as e:
        flash(f"Delete failed: {str(e)}")
    return redirect(url_for("platform"))


# Ensure seed data when Supabase is configured
if __import__("os").environ.get("SUPABASE_URL") or __import__("os").environ.get("SUPABASE_SERVICE_ROLE_KEY"):
    try:
        ensure_seed_data()
    except Exception:
        pass


if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", "8000"))
    print("\n  Open in browser:  http://127.0.0.1:{port}  or  http://localhost:{port}\n".format(port=port))
    app.run(host="0.0.0.0", port=port, debug=True)
