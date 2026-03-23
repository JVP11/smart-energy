# Smart Energy Platform — Everything Explained

A complete guide to what this project is, what each part does, and how it all fits together.

---

## 1. What Is This Project?

**Smart Energy Platform** is a **DBMS (Database Management System) college project** — a web app for energy management in Kerala.

- **Purpose:** Help consumers track electricity usage, estimate bills, and report power outages; help admins manage data and analyze reports.
- **Tech:** Python Flask (backend), Supabase/PostgreSQL (database), HTML/CSS/JS (frontend).
- **Live:** https://smart-energy-eykr.onrender.com

---

## 2. Who Uses It?

| Role | Who | What they do |
|------|-----|--------------|
| **User** | Consumer | Register, add appliance usage, view bills, set budget, manage facilities, report outages on map |
| **Admin** | Platform manager | Add/edit appliances & tariffs, manage bills, view database, add map markers, Power Analyst dashboard |

---

## 3. Main Pages & Features

### Home (`/`)
- Landing page with login/register.
- Description of the platform.

### Login (`/login`)
- Username = admin username **or** user email.
- Password.
- Redirects to Admin Dashboard or User Platform.

### Register (`/register`)
- Name, email, password.
- Creates a `users` row in the database.
- Redirects to login.

### User Platform (`/platform`) — for consumers
- **User Dashboard:** Add appliance usage (pick appliance, hours/day, days), view usage records, view bills.
- **Usage:** Track which appliance, how many hours, how many days.
- **Bill:** Calculated from usage using KSEB rules (slabs, fixed charges).
- **Budget:** Set monthly budget to compare with estimated bill.
- **Facilities:** Add buildings/zones (e.g. home, office).
- **Kerala Power Map:** Link to the map for outage reporting.

### Admin Dashboard (`/admin/dashboard`) — for admins
- **Appliances:** Add/edit/delete appliances (name, power in watts).
- **Tariffs:** Add/edit tariff rates (₹/kWh, effective date).
- **Bills:** View all user bills, delete if needed.
- **Power Map:** Open Kerala map.
- **Power Analyst:** Stats, charts, filters, CSV export of reports.
- **Database Schema:** View tables and row counts.

### Kerala Power Map (`/map/kerala-power`)
- **Map:** Kerala with power infrastructure (towers, poles, substations, lines) from OpenStreetMap.
- **Search:** Type place name (e.g. Trivandrum, Kochi), get suggestions, zoom to location.
- **Locate me:** Button to zoom to your GPS location.
- **Report outage (users):** Click "Report outage" → click on map → add description → submit.
- **Admin markers:** Admins can add markers (Issue, Maintenance, OK).
- **Report markers:** Red = no current, Orange = issue, Gray = resolved.

### Power Analyst (`/admin/map/reports`) — admins only
- **Stats:** Total reports, Pending, Inspected, Resolved.
- **Charts:** Breakdown by status and report type.
- **Filters:** By status, by type.
- **Table:** All reports with Inspected/Resolved actions.
- **Export:** Download CSV.

### Database Schema (`/admin/data`) — admins only
- **Table overview:** ER diagram, table definitions, relationships.
- **Row counts:** Live counts for each table.
- **Normalization:** 3NF description.

---

## 4. Database — What Is Stored?

### Tables

| Table | What it stores |
|-------|----------------|
| **admins** | Admin usernames and passwords |
| **users** | Consumer name, email, password, monthly budget |
| **appliances** | Catalog: appliance name, power (watts) |
| **tariffs** | Electricity rate (₹/kWh), effective date |
| **usage** | User + appliance + hours/day + days (links users to appliances) |
| **bills** | User, total units, total cost, date (calculated from usage) |
| **facilities** | User buildings/zones (name, type, zone) |
| **power_reports** | Lat, lng, report type, description, status, who reported (user/admin) |

### Relationships
- **users** → usage, bills, facilities, power_reports (one user, many records).
- **admins** → power_reports (admin markers).
- **appliances** → usage (one appliance, many usages).

---

## 5. Important Files

| File | Purpose |
|------|---------|
| `dbms.py` | Main app: all routes, logic, API endpoints |
| `config.py` | Supabase client setup |
| `kseb.py` | KSEB bill calculation rules |
| `app.py` | Entry point: imports `dbms` for Gunicorn/Render |
| `supabase_schema.sql` | Full database schema + seed data |
| `supabase_migration_power_reports.sql` | Migration for power_reports table |
| `requirements.txt` | Python dependencies |
| `templates/*.html` | HTML pages (Jinja2) |
| `static/style.css` | Styling |
| `tests/test_routes.py` | Route tests |

---

## 6. APIs (Backend Endpoints)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/overpass` | GET | Proxy to Overpass API for map power data |
| `/api/geocode` | GET | Search places (Nominatim) for map search |
| `/api/map/power-reports` | GET | Power reports as JSON for map markers |
| `/map/report` | POST | User submits outage report |
| `/admin/map/marker` | POST | Admin adds marker |
| `/health` | GET | Check if Supabase is configured |

---

## 7. Load Calculation — What It Is & What It’s Used For

**Load Calculation** is in the **Platform → Load Calculation** tab.

### What it is
An NEC-style electrical load calculator that estimates the **demand load** (peak power) and suggests **panel/cable sizing**.

### Inputs
| Input | What it is | Example |
|-------|------------|---------|
| **Connected Load (W)** | Sum of all appliance power ratings (watts) when everything could be on | 5000 W (fan + TV + fridge + lights + AC) |
| **Demand Factor (0–1)** | Fraction of connected load that actually runs at peak (not everything runs together) | 0.8 = 80% |
| **Voltage (V)** | Supply voltage (India: 230 V) | 230 V |

### Outputs
| Output | What it is | Example |
|--------|------------|---------|
| **Connected Load** | Same as input | 5000 W |
| **Demand Load** | Connected Load × Demand Factor | 4000 W |
| **Suggested Amperage** | Demand Load ÷ Voltage | 17.4 A |
| **Min Panel (A)** | Rounded up to standard breaker size (nearest 10 A) | 20 A |

### What it’s used for
- **Panel sizing** — What main circuit breaker (MCB) or panel size to install
- **Cable sizing** — What wire gauge for that current
- **Safety** — Avoid overloading circuits
- **Compliance** — Similar to NEC (National Electrical Code) principles

### Where it lives
- **Tab:** Platform → Load Calculation (client-side JavaScript)
- **Logic:** In `templates/platform.html` (lines ~350–363)

### What is NEC?

| Term | What it is | Simple meaning |
|------|------------|----------------|
| **NEC** | National Electrical Code (USA) | Rules for safe electrical wiring and installation |
| **NEC compliance** | Following those rules | Sizing wires, breakers, panels so they don’t overload |
| **Connected load** | Sum of all appliance power ratings | Total power if everything ran at once (e.g. all fans, ACs, TVs on) |
| **Demand load** | Connected load × demand factor | Realistic peak load (not everything on at the same time) |
| **Demand factor** | A fraction between 0 and 1 | How much of the connected load typically runs together (e.g. 0.8 = 80%) |
| **Amperage (A)** | Current in Amperes | Flow of electricity; wires and breakers are rated in Amps |
| **Panel / MCB** | Main circuit breaker | Cuts power when current is too high; must be rated for demand load |
| **Cable sizing** | Choosing wire thickness | Thicker wire for higher current; NEC tables specify this |

**NEC in short:** The USA’s standard for safe electrical design. The Load Calculation in this app follows similar ideas (demand load, panel size) even though it’s for Kerala. India uses the Indian Electricity Rules and IS codes; the logic is similar.

### NEC Load Classification

**Load classification** = grouping electrical loads by NEC rules so engineers can correctly calculate:
- electrical demand
- wire size
- breaker rating
- safety protection
- power distribution design

| Classification | Description | NEC rule / example |
|----------------|-------------|--------------------|
| **General Lighting** | Lights, fans, plug points | 3 VA per sq.ft (residential) |
| **Small Appliance** | Kitchen/dining (mixer, toaster, microwave) | 1500 VA per circuit |
| **Continuous Load** | Runs 3+ hours continuously | 125% of actual load |
| **Non-Continuous** | Runs &lt; 3 hours | 100% load |
| **Motor Load** | Pumps, elevators, HVAC | Special starting-current factors |
| **Heating & AC** | Electric heaters, air conditioners | Calculated separately |

**Example (1000 sq.ft house):**
1. General lighting: 1000 × 3 = 3000 VA
2. Small appliance (2 circuits): 2 × 1500 = 3000 VA
3. Continuous adjustment: 3000 × 125% = 3750 VA
4. **Total classified load: 6750 VA** → used for breaker size, wiring, demand load.

---

## 8. How Bill Calculation Works

- User adds usage: appliance + hours/day + days.
- **Units (kWh)** = (watts × hours × days) / 1000.
- **Bill** uses KSEB slabs in `kseb.py` (fixed charges + slab rates).
- Stored in `bills` table.

---

## 9. How the Map Works

1. **Base map:** Leaflet.js + OpenStreetMap tiles.
2. **Power infrastructure:** Overpass API (OSM) → towers, poles, substations, lines.
3. **If OSM fails:** Demo substations (Trivandrum, Kochi, etc.) and sample lines.
4. **Place search:** Nominatim geocoding (restricted to Kerala).
5. **Reports:** From `power_reports` table, shown as markers by type/status.

---

## 10. Environment Variables

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase API key (JWT format) |
| `SECRET_KEY` | Flask session signing |
| `PORT` | Server port (default 8000; Render sets this) |

---

## 11. Default Credentials

- **Admin:** username `admin`, password `admin123`
- **User:** Register first, then login with email

---

## 12. Deployment (Render)

1. Push code to GitHub.
2. Render connects repo, runs `pip install -r requirements.txt`.
3. Start command: `gunicorn -b 0.0.0.0:$PORT dbms:app`
4. Environment variables set in Render dashboard.
5. Live URL: https://smart-energy-eykr.onrender.com

---

## 13. What Each Thing Is & What It’s Used For

### Technologies

| Thing | What it is | Used for |
|-------|------------|----------|
| **Flask** | Python web framework | Backend server, routes, sessions, templates |
| **Supabase** | Hosted PostgreSQL + API | Database for all app data |
| **PostgreSQL** | Relational database | Tables, relationships, queries (via Supabase) |
| **Gunicorn** | WSGI HTTP server | Runs the Flask app in production (Render) |
| **Jinja2** | Template engine (built into Flask) | Insert data into HTML (e.g. `{{ user_name }}`) |
| **Leaflet.js** | JavaScript map library | Display and interact with maps |
| **OpenStreetMap** | Map tiles and data | Map background, power towers/lines, places |
| **Chart.js** | JavaScript chart library | Power Analyst charts (status, type) |
| **Nominatim** | Geocoding service | Turn place names into lat/lng for search |
| **Overpass API** | Query OpenStreetMap | Fetch power towers, poles, substations, lines |
| **Render** | Cloud hosting | Run the app 24/7 on the internet |
| **Git / GitHub** | Version control and repo | Code storage, deploy trigger for Render |

### Project Files

| File | What it is | Used for |
|------|------------|----------|
| `dbms.py` | Main Python application | Routes, logic, API endpoints, page handlers |
| `config.py` | Configuration module | Create Supabase client from env vars |
| `kseb.py` | Bill calculation logic | KSEB slab rates and fixed charges |
| `app.py` | Entry point | Import and expose the app for Gunicorn |
| `requirements.txt` | Dependency list | `pip install -r requirements.txt` |
| `supabase_schema.sql` | SQL script | Create tables and load default data |
| `supabase_migration_power_reports.sql` | SQL migration | Add `power_reports` table |
| `.env` | Env vars (not in git) | Store Supabase URL, key, secret locally |
| `Procfile` | Process config | Tells Render how to start the app |
| `render.yaml` | Deployment config | Render service blueprint |

### Folders & Static Files

| Thing | What it is | Used for |
|-------|------------|----------|
| `templates/` | HTML templates | Page layout and structure |
| `static/style.css` | Stylesheet | Look and feel of the site |
| `tests/` | Test directory | Pytest route tests |

### Database Tables

| Table | What it is | Used for |
|-------|------------|----------|
| `admins` | Admin login data | Check admin username/password |
| `users` | Consumer accounts | Registration, login, profile, budget |
| `appliances` | Appliance catalog | List of devices and their power (W) |
| `tariffs` | Electricity rates | Bill calculation (₹/kWh) |
| `usage` | Usage records | Link user + appliance + hours + days |
| `bills` | Bill records | Stored calculated bills per user |
| `facilities` | Buildings/zones | Group usage by location |
| `power_reports` | Outage reports | Map markers: location, type, status |

### APIs & External Services

| Thing | What it is | Used for |
|-------|------------|----------|
| `/api/overpass` | Backend proxy | Call Overpass from frontend (avoid CORS) |
| `/api/geocode` | Backend geocoding | Search places in Kerala for the map |
| `/api/map/power-reports` | JSON endpoint | Load outage markers for the map |
| **Overpass** | OSM query API | Get power towers, poles, substations, lines |
| **Nominatim** | OSM geocoding | Convert place names to coordinates |

### Concepts

| Concept | What it is | Used for |
|---------|------------|----------|
| **UUID** | Unique ID (e.g. `abc-123-...`) | Primary key for rows in tables |
| **Foreign key** | Reference to another table’s ID | Relationships (e.g. usage → user, appliance) |
| **ON DELETE CASCADE** | Delete linked rows when parent is deleted | Clean up usage when user is deleted |
| **Session** | Server-side user state | Remember who is logged in |
| **CSV export** | Comma-separated text file | Download Power Analyst data for Excel |

---

## 14. Plain-Language Glossary — What Everything Means

Every term used in the project, explained simply.

### General & Project

| Term | What it is | Simple meaning |
|------|------------|----------------|
| **DBMS** | Database Management System | Software that stores and manages data in tables |
| **Flask** | Python web framework | Tool to build web apps (routes, pages, APIs) |
| **Backend** | Server-side code | Runs on the server; handles data, logic, database |
| **Frontend** | Client-side code | Runs in the browser; what the user sees and clicks |
| **API** | Application Programming Interface | Way for one program to talk to another (e.g. frontend asks backend for data) |
| **Deploy** | Put app on internet | Make it live so anyone can visit it |
| **Render** | Cloud hosting platform | Company that runs your app 24/7 on their servers |
| **Supabase** | Database-as-a-service | Cloud PostgreSQL; you store data, they handle servers |
| **PostgreSQL** | Relational database | Stores data in tables with rows and columns |
| **Jinja2** | Template engine | Puts variables (e.g. `{{ name }}`) into HTML |
| **Gunicorn** | WSGI server | Runs Flask in production (handles many users) |

### Electrical & Billing

| Term | What it is | Simple meaning |
|------|------------|----------------|
| **NEC** | National Electrical Code (USA) | Safety rules for wiring, panels, cables |
| **Watts (W)** | Unit of power | How much electricity an appliance uses |
| **kWh** | Kilowatt-hour | Unit of energy; 1 kWh = 1000 W for 1 hour |
| **Ampere (A)** | Unit of current | Flow of electricity; breakers/wires are rated in Amps |
| **Voltage (V)** | Electrical pressure | India: 230 V; USA: 120 V |
| **KSEB** | Kerala State Electricity Board | Kerala's electricity utility; sets tariff rates |
| **Tariff** | Price per unit | ₹/kWh (how much you pay per kWh) |
| **Telescopic slab** | Tiered pricing | Different rates for different usage ranges (e.g. 0–50 units cheaper than 201–250) |
| **Fixed charge** | Monthly fee | Base amount regardless of usage |
| **Fuel surcharge** | Extra per unit | Small extra charge (e.g. ₹0.10/unit) |
| **Electricity duty** | Tax | 10% on energy + fuel (government tax) |
| **Bi-monthly** | Every 2 months | KSEB bills every 60 days |
| **Connected load** | Sum of all appliance power | Total W if everything ran at once |
| **Demand load** | Realistic peak | Connected load × demand factor |
| **Demand factor** | Peak usage fraction | 0.8 = 80% of connected load typically runs |
| **MCB** | Miniature Circuit Breaker | Trips when current is too high; protects wiring |
| **Panel** | Main distribution board | Holds breakers; connects meter to house circuits |

### Database

| Term | What it is | Simple meaning |
|------|------------|----------------|
| **Table** | Data stored in rows and columns | Like a spreadsheet (e.g. `users`, `bills`) |
| **Row** | One record | One user, one bill, one usage entry |
| **Column** | One field | e.g. `name`, `email`, `total_cost` |
| **Primary key (PK)** | Unique ID for each row | No two rows have the same PK (e.g. `id`) |
| **Foreign key (FK)** | Link to another table | e.g. `user_id` in `usage` points to `users.id` |
| **UUID** | Universally unique ID | Long random string like `a1b2c3d4-...` |
| **ON DELETE CASCADE** | Auto-delete children | If user deleted, delete their usage too |
| **ON DELETE SET NULL** | Clear the link | If user deleted, set `user_id` to null (keep report) |
| **3NF** | Third Normal Form | No repeated data; each fact stored once |
| **Normalization** | Organizing data | Splitting tables to avoid redundancy |
| **ER diagram** | Entity-Relationship diagram | Picture of tables and how they connect |
| **Migration** | SQL script to change schema | Add a new table or column |

### Map & Reports

| Term | What it is | Simple meaning |
|------|------------|----------------|
| **Leaflet** | JavaScript map library | Draws maps, markers, lines in the browser |
| **OpenStreetMap (OSM)** | Free map data | Like Wikipedia for maps; anyone can edit |
| **Overpass API** | Query OSM | Get specific things (e.g. power towers) from OSM |
| **Geocoding** | Address → coordinates | Turn "Trivandrum" into lat/lng |
| **Nominatim** | OSM geocoding service | Free place search |
| **Substation** | Electricity switching station | Steps voltage up/down; connects grid to area |
| **Power line** | Transmission/distribution line | Cable that carries electricity |
| **Power tower / pole** | Structure holding wires | Towers (high voltage), poles (local) |
| **lat, lng** | Latitude, longitude | Coordinates on Earth (e.g. 10.5, 76.2 for Kerala) |
| **Marker** | Pin on map | Red dot for outage, orange for issue, etc. |
| **Power report** | Outage / issue record | User or admin marks "no current" or "maintenance" on map |
| **report_type** | Kind of report | no_current, issue, maintenance, ok |
| **status** | Workflow state | pending → inspected → resolved |

### Platform Tabs

| Tab | What it is | Simple meaning |
|-----|------------|----------------|
| **Load Calculation** | NEC-style panel sizing | Enter connected load; get suggested breaker size |
| **Infrastructure** | Facilities + map link | Your buildings/zones + link to Kerala Power Map |
| **Energy Modeling** | Usage and bill estimate | Add appliance usage; see estimated kWh and bill |
| **KSEB Rules** | Kerala tariff calculator | Enter units; see slab breakdown and total bill |
| **Facility Management** | Budget, alerts | Set monthly budget; see remaining; carbon footprint |

### Other

| Term | What it is | Simple meaning |
|------|------------|----------------|
| **Facility** | Building or zone | Home, office, Zone A — to group usage |
| **Usage record** | One appliance, hours, days | e.g. "Ceiling Fan, 6 hrs/day, 30 days" |
| **Bill** | Calculated cost | Stored total for a period (units × rates + fixed + duty) |
| **Power Analyst** | Admin report dashboard | Stats, charts, filters, CSV of outage reports |
| **Session** | Logged-in state | Server remembers you until logout |
| **CORS** | Cross-Origin Resource Sharing | Browser rule; proxy avoids "blocked by CORS" |
| **Procfile** | Process file | Tells Render: run this command to start the app |
| **requirements.txt** | Python package list | `pip install -r requirements.txt` installs all |
| **.env** | Environment file | Secrets (keys, URLs) — not committed to Git |
| **JWT** | JSON Web Token | One format for API keys (starts with `eyJ...`) |

---

## 15. Summary

| Part | What it is |
|------|------------|
| **Project type** | DBMS college project |
| **App** | Web-based energy management for Kerala |
| **Users** | Consumers (usage, bills, outage reports) |
| **Admins** | Manage appliances, tariffs, bills, Power Analyst |
| **Database** | Supabase (PostgreSQL) – 8 tables |
| **Map** | Kerala + power infrastructure + outage reports |
| **Bill logic** | KSEB-style slabs and fixed charges |
