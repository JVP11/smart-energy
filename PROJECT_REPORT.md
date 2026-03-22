# Smart Energy Platform — DBMS Project Report

---

## 1. PROBLEM STATEMENT

Energy consumers in Kerala lack a unified system to:

1. **Track electricity usage** — Manually recording appliance hours and estimating consumption is error-prone.
2. **Estimate bills** — Understanding KSEB slab rates and calculating bills is complex.
3. **Monitor budgets** — No easy way to set monthly limits and compare with actual/estimated consumption.
4. **Report outages** — Power cuts and line faults are reported by phone or in person; there is no map-based, location-specific reporting.
5. **Manage facilities** — Consumers with multiple buildings or zones cannot organize usage by location.
6. **Admin visibility** — Utilities and administrators lack a single dashboard to see outage reports, infrastructure markers, and analytics.

**Current gaps:** Paper bills, manual logs, disconnected complaint systems, and no central database for consumption and outage data.

---

## 2. INTRODUCTION

Smart Energy Platform is a web-based Database Management System for energy management in Kerala. It uses **Flask** (Python) and **Supabase (PostgreSQL)** to provide:

- User registration and authentication
- Appliance catalog and usage tracking
- KSEB-style bill calculation
- Facility management (buildings, zones)
- Kerala Power Map with outage reporting and infrastructure markers
- Admin dashboard for appliances, tariffs, bills, and Power Analyst (stats, charts, CSV export)

**Live demo:** https://smart-energy-eykr.onrender.com

---

## 3. PROPOSED SYSTEM

### 3.1 For Consumers (Energy Users)

- **Registration and login** — Create account with name, email, password.
- **Usage tracking** — Select appliances (fan, AC, TV, etc.), enter hours per day and number of days.
- **Bill estimation** — Automatic calculation using KSEB slab rates.
- **Budget setting** — Set monthly budget and compare with estimated bill.
- **Facility management** — Add buildings/zones and organize usage.
- **Outage reporting** — On Kerala map: search place, click location, describe issue, submit report.

### 3.2 For Reporters (Map Users)

- **Kerala Power Map** — View power infrastructure (towers, poles, substations, lines).
- **Place search** — Search cities/towns and zoom to location.
- **Locate me** — Use GPS to find current location.
- **Report no current** — Mark outage location on map with description.
- **View reports** — See own and other reports (pending, inspected, resolved).

### 3.3 For Administrators

- **Appliance catalog** — Add, edit, delete appliances with power ratings.
- **Tariff management** — Add, edit, delete tariff rates and effective dates.
- **Bill management** — View and delete user bills.
- **Map markers** — Add Issue, Maintenance, OK markers on Kerala map.
- **Power Analyst** — View stats (total, pending, inspected, resolved), charts, filters, CSV export.
- **Report workflow** — Mark reports as Inspected or Resolved.
- **Database schema** — View tables, relationships, row counts.

### 3.4 Overall Benefits

- **Single platform** for usage, bills, and outage reporting.
- **Database-backed** — All data in PostgreSQL with referential integrity.
- **Map-based reporting** — Location-specific outage data for faster response.
- **Admin analytics** — Aggregate data for decision-making.
- **Transparency** — Consumers see usage and estimated costs clearly.
- **Scalability** — Cloud hosting (Render) and managed database (Supabase).

---

## 4. DATABASE DESIGN

### 4.1 Table Design

| Table | Attributes | Primary Key | Foreign Keys |
|-------|------------|-------------|--------------|
| **admins** | id, username, password | id (UUID) | — |
| **users** | id, name, email, password, monthly_budget | id (UUID) | — |
| **appliances** | id, appliance_name, power_rating_watts | id (UUID) | — |
| **tariffs** | id, rate_per_kwh, effective_date | id (UUID) | — |
| **usage** | id, user_id, appliance_id, hours_per_day, number_of_days | id (UUID) | user_id→users, appliance_id→appliances |
| **bills** | id, user_id, total_units, total_cost, bill_date | id (UUID) | user_id→users |
| **facilities** | id, user_id, name, type, zone | id (UUID) | user_id→users |
| **power_reports** | id, lat, lng, report_type, description, status, reporter_type, user_id, admin_id, created_at | id (UUID) | user_id→users, admin_id→admins |

**Constraints:** UNIQUE (users.email, admins.username); ON DELETE CASCADE (usage, bills, facilities); ON DELETE SET NULL (power_reports).

### 4.2 ER Diagram

```
                    ┌─────────────┐
                    │   admins    │
                    │ id (PK)     │
                    │ username    │
                    │ password    │
                    └──────┬──────┘
                           │
                           │ 1:N
                           ▼
┌─────────────┐       ┌─────────────────┐
│   users     │       │  power_reports   │
│ id (PK)     │───────│ user_id (FK)    │
│ name        │  1:N  │ admin_id (FK)   │
│ email       │       │ lat, lng        │
│ password    │       │ report_type     │
│ monthly_    │       │ status          │
│ budget      │       └─────────────────┘
└──────┬──────┘
       │
       ├──────────1:N────────►┌─────────────┐
       │                      │   usage     │
       │                      │ user_id(FK) │
       │                      │ appliance_id│
       │                      └──────┬──────┘
       │                             │ N:1
       │                             ▼
       ├──────────1:N────────►┌─────────────┐     ┌─────────────┐
       │                      │ appliances  │     │  tariffs    │
       │                      │ id (PK)     │     │ id (PK)     │
       │                      │ name        │     │ rate_per_kwh│
       │                      │ power_watts │     │ effective_dt│
       │                      └─────────────┘     └─────────────┘
       │
       ├──────────1:N────────►┌─────────────┐
       │                      │   bills     │
       │                      │ user_id(FK) │
       │                      │ total_units │
       │                      │ total_cost  │
       │                      └─────────────┘
       │
       └──────────1:N────────►┌─────────────┐
                              │ facilities  │
                              │ user_id(FK) │
                              │ name, type  │
                              └─────────────┘
```

---

## 5. IMPLEMENTATION DETAILS

### 5.1 System Requirements and Specification

#### 5.1.1 Hardware Specification

- **Development:** Any PC/laptop with 2GB+ RAM, internet connection.
- **Production:** Cloud (Render) — managed hosting.
- **Database:** Supabase (PostgreSQL) — managed cloud database.

#### 5.1.2 Software Specification

- **OS:** Windows, Linux, or macOS (development).
- **Python:** 3.10+
- **Package manager:** pip
- **Version control:** Git
- **Deployment:** Render (PaaS)

#### 5.1.3 Frontend

- **HTML5** — Page structure (Jinja2 templates).
- **CSS** — Styling (custom `style.css`).
- **JavaScript** — Map (Leaflet.js), search, forms.
- **Libraries:** Leaflet 1.9.4 (map), Chart.js (Power Analyst charts), OpenStreetMap tiles.

#### 5.1.4 Backend and Database

- **Backend:** Python 3.10, Flask 3.x.
- **Database:** Supabase (PostgreSQL).
- **ORM/Client:** Supabase Python client (`supabase` package).
- **APIs:** Overpass (power infrastructure), Nominatim (geocoding).
- **WSGI:** Gunicorn (production).

### 5.2 System Implementation

- **Routes:** Flask routes for all pages and APIs (`dbms.py`).
- **Templates:** Jinja2 HTML in `templates/`.
- **Database:** Schema in `supabase_schema.sql`, migration in `supabase_migration_power_reports.sql`.
- **Bill logic:** KSEB rules in `kseb.py`.
- **Config:** Environment variables (`.env`) for Supabase URL, key, secret.
- **Deploy:** `render.yaml`, `Procfile`, `requirements.txt`.

---

## 6. RESULTS

- **Working application** deployed at https://smart-energy-eykr.onrender.com
- **Database** with 8 tables, referential integrity, 3NF
- **User flow:** Register → Login → Add usage → View bills → Report outages on map
- **Admin flow:** Login → Manage appliances/tariffs/bills → Power Analyst → Mark reports
- **Map:** Kerala with power infrastructure, search, locate me, outage reports
- **Power Analyst:** Stats, charts, filters, CSV export
- **Tests:** `pytest` for key routes (6 tests passing)

---

## References

- Flask: https://flask.palletsprojects.com/
- Supabase: https://supabase.com
- Leaflet: https://leafletjs.com
- OpenStreetMap: https://www.openstreetmap.org
- KSEB: Kerala State Electricity Board tariff structure
