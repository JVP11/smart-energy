# Smart Energy Platform — DBMS Project

**Database Management System Project** — College project demonstrating database design, schema, relationships, and SQL operations for an energy management platform.

**Live demo:** [https://smart-energy-eykr.onrender.com](https://smart-energy-eykr.onrender.com)

---

## Project Overview

A **web-based energy management system** for Kerala, built with **Flask** and **Supabase (PostgreSQL)**. The project showcases DBMS concepts: schema design, normalization, referential integrity, CRUD operations, and analytical queries.

### Features
- User registration, login, and admin dashboard
- Appliance catalog and usage tracking
- Bill calculation (KSEB rules)
- Facility management (buildings, zones)
- Power outage reporting with Kerala map
- Admin analyst dashboard with stats and CSV export

---

## Database Schema

### ER Diagram (Entity-Relationship)

```
┌─────────────┐       ┌─────────────┐
│   admins    │       │   users     │
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ username    │       │ name        │
│ password    │       │ email       │
└──────┬──────┘       │ password    │
       │              │ monthly_budget│
       │              └──────┬──────┘
       │                     │
       │              ┌──────┴───────────────────────────┐
       │              │                                 │
       ▼              ▼                                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│power_reports│  │   usage     │  │   bills     │  │  facilities  │
├─────────────┤  ├─────────────┤  ├─────────────┤  ├─────────────┤
│ id (PK)     │  │ id (PK)     │  │ id (PK)     │  │ id (PK)     │
│ lat, lng    │  │ user_id(FK) │  │ user_id(FK) │  │ user_id(FK) │
│ report_type │  │ appliance_id│  │ total_units │  │ name        │
│ status      │  │ hours_per_day│ │ total_cost  │  │ type        │
│ user_id(FK) │  │ number_of_days│ │ bill_date   │  │ zone        │
│ admin_id(FK)│  └──────┬──────┘  └─────────────┘  └─────────────┘
└─────────────┘         │
                        ▼
                 ┌─────────────┐  ┌─────────────┐
                 │ appliances  │  │  tariffs    │
                 ├─────────────┤  ├─────────────┤
                 │ id (PK)     │  │ id (PK)     │
                 │ appliance_name│ │ rate_per_kwh│
                 │ power_rating_watts│effective_date│
                 └─────────────┘  └─────────────┘
```

### Tables and Relationships

| Table | Primary Key | Foreign Keys | Description |
|-------|-------------|--------------|-------------|
| admins | id (UUID) | — | Admin users for platform management |
| users | id (UUID) | — | Registered energy consumers |
| appliances | id (UUID) | — | Appliance catalog (power ratings) |
| tariffs | id (UUID) | — | Electricity rate per kWh |
| usage | id (UUID) | user_id → users, appliance_id → appliances | User appliance usage records |
| bills | id (UUID) | user_id → users | Bill history per user |
| facilities | id (UUID) | user_id → users | User facilities (buildings, zones) |
| power_reports | id (UUID) | user_id → users, admin_id → admins | Outage reports and map markers |

### Normalization
- **3NF**: Tables are in Third Normal Form — no transitive dependencies
- **Referential integrity**: ON DELETE CASCADE for usage, bills, facilities; ON DELETE SET NULL for power_reports

---

## SQL Files

- **supabase_schema.sql** — Full schema (CREATE TABLE, constraints, seed data)
- **supabase_migration_power_reports.sql** — Migration for power_reports table

---

## Setup

1. Install: `pip install -r requirements.txt`
2. Create `.env`:
   ```
   SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   SECRET_KEY=your-secret
   ```
3. Run **supabase_schema.sql** in Supabase SQL Editor (Dashboard → SQL Editor)
4. Run **supabase_migration_power_reports.sql** if power_reports is missing
5. Run **supabase_migration_load_kseb.sql** if load_calculations and kseb_estimates are missing
6. Start: `python3 dbms.py` (default port 8000)
7. Open http://127.0.0.1:8000

Use `PORT=9000 python3 dbms.py` if 8000 is in use.

**Can't reach the app?** Try:
- http://127.0.0.1:8000
- http://localhost:8000
- If on LAN: http://YOUR_IP:8000 (run `hostname -I` to see IP)

---

## Default Login

- **Admin:** `admin` / `admin123`
- **User:** Register → login with email

---

## DBMS Operations Demonstrated

- **CREATE / INSERT** — User registration, appliance usage, bills, power reports
- **SELECT** — Dashboard queries, filters, joins (usage + appliances)
- **UPDATE** — Edit usage, tariffs, appliances; mark reports as inspected/resolved
- **DELETE** — Admin deletes bills, appliances, tariffs; users delete usage
- **Aggregation** — Power Analyst: COUNT by status/type, CSV export
- **Constraints** — UNIQUE (email, username), NOT NULL, CHECK, REFERENCES

---

## Tests

```bash
python3 -m pytest tests/ -v
```
