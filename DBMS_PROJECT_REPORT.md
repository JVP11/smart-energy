# DBMS Project Report
## Smart Energy Platform — Energy Management System for Kerala

---

### Title
**Smart Energy Platform: A Web-Based Database Management System for Energy Consumption Tracking and Power Outage Reporting**

### Submitted by
[Your Name]

### Course
Database Management Systems (DBMS)

### Institution
[Your College/University]

### Date
[Submission Date]

---

## Table of Contents
1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Objectives](#3-objectives)
4. [System Design](#4-system-design)
5. [Database Design](#5-database-design)
6. [Implementation](#6-implementation)
7. [Screenshots and Modules](#7-screenshots-and-modules)
8. [Conclusion](#8-conclusion)
9. [References](#9-references)
10. [Appendix](#10-appendix)

---

## 1. Abstract

Smart Energy Platform is a web-based database management system built for energy consumption tracking, bill calculation, facility management, and power outage reporting. The system uses **Flask** (Python) for the application layer and **Supabase (PostgreSQL)** for the database. It demonstrates core DBMS concepts: relational schema design, normalization, referential integrity, CRUD operations, and analytical queries. The platform serves energy consumers in Kerala and supports KSEB-style billing rules.

**Live Demo:** [https://smart-energy-eykr.onrender.com](https://smart-energy-eykr.onrender.com)

---

## 2. Introduction

### 2.1 Background

Energy management systems help consumers track electricity usage, estimate bills, and manage facilities. Power utilities benefit from crowd-sourced outage reports for faster response. This project combines both: a consumer-facing platform for usage and bills, plus a map-based power outage reporting system.

### 2.2 Scope

- User registration and authentication
- Appliance catalog and usage tracking
- Bill calculation (KSEB rules)
- Facility management (buildings, zones)
- Power outage reporting on Kerala map
- Admin dashboard (appliances, tariffs, bills, reports)
- Analyst dashboard (stats, charts, filters, CSV export)

### 2.3 Technology Stack

| Layer        | Technology                |
|-------------|----------------------------|
| Frontend    | HTML, CSS, JavaScript     |
| Backend     | Python, Flask             |
| Database    | PostgreSQL (Supabase)     |
| Deployment  | Render.com               |

---

## 3. Objectives

1. Design a normalized relational schema for energy management
2. Implement CRUD operations (Create, Read, Update, Delete)
3. Enforce referential integrity using foreign keys
4. Demonstrate aggregation and analytical queries
5. Provide a working web application with database integration

---

## 4. System Design

### 4.1 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│   Flask     │────▶│  Supabase   │
│  (Client)   │◀────│   (Server)  │◀────│ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
```

### 4.2 User Roles

- **User:** Register, add usage, view bills, set budget, manage facilities, report outages on map
- **Admin:** Manage appliances, tariffs, bills; add map markers; Power Analyst dashboard

---

## 5. Database Design

### 5.1 Entity-Relationship Diagram

```
                    ┌─────────────┐
                    │   admins    │
                    │ id (PK)     │
                    │ username    │
                    │ password    │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐  ┌─────────────┐  ┌─────────────────┐
│  power_reports  │  │   users     │  │  power_reports  │
│ id (PK)         │  │ id (PK)     │  │ (admin_id FK)    │
│ admin_id (FK)   │  │ name        │  └─────────────────┘
└─────────────────┘  │ email       │
                     │ password    │
                     │ monthly_budget│
                     └──────┬──────┘
                            │
    ┌───────────────┬───────┼───────┬───────────────┐
    │               │       │       │               │
    ▼               ▼       ▼       ▼               ▼
┌─────────┐  ┌─────────┐ ┌─────┐ ┌─────────┐  ┌──────────┐
│ usage   │  │ bills   │ │facil│ │power_rep│  │facilities │
│ user_id │  │ user_id │ │ities│ │user_id  │  │ user_id   │
│ app_id  │  └─────────┘ └─────┘ └─────────┘  └──────────┘
└────┬────┘
     │
     ▼
┌─────────────┐     ┌─────────────┐
│ appliances  │     │  tariffs    │
│ id (PK)     │     │ id (PK)     │
│ appliance_  │     │ rate_per_   │
│ name        │     │ kwh        │
│ power_rating│     │ effective_  │
└─────────────┘     │ date        │
                    └─────────────┘
```

### 5.2 Tables and Attributes

| Table | Attributes | Primary Key | Description |
|-------|------------|-------------|-------------|
| **admins** | id, username, password | id (UUID) | Admin authentication |
| **users** | id, name, email, password, monthly_budget | id (UUID) | Consumer registration |
| **appliances** | id, appliance_name, power_rating_watts | id (UUID) | Appliance catalog |
| **tariffs** | id, rate_per_kwh, effective_date | id (UUID) | Electricity rate (₹/kWh) |
| **usage** | id, user_id, appliance_id, hours_per_day, number_of_days | id (UUID) | User appliance usage |
| **bills** | id, user_id, total_units, total_cost, bill_date | id (UUID) | Calculated bills |
| **facilities** | id, user_id, name, type, zone | id (UUID) | User facilities |
| **power_reports** | id, lat, lng, report_type, description, status, reporter_type, user_id, admin_id, created_at | id (UUID) | Outage reports / map markers |

### 5.3 Relationships and Cardinality

| Relationship | Cardinality | Foreign Key | Delete Rule |
|-------------|-------------|-------------|------------|
| users → usage | 1:N | usage.user_id | CASCADE |
| users → bills | 1:N | bills.user_id | CASCADE |
| users → facilities | 1:N | facilities.user_id | CASCADE |
| users → power_reports | 1:N | power_reports.user_id | SET NULL |
| admins → power_reports | 1:N | power_reports.admin_id | SET NULL |
| appliances → usage | 1:N | usage.appliance_id | — |

### 5.4 Constraints

- **Primary keys:** UUID on all tables
- **UNIQUE:** users.email, admins.username
- **NOT NULL:** Essential columns (name, email, lat, lng, etc.)
- **REFERENCES:** All foreign keys with appropriate ON DELETE behavior

### 5.5 Normalization

- **3NF (Third Normal Form):** All tables are in 3NF
- No transitive dependencies
- No repeating groups
- Each non-key attribute depends only on the primary key

---

## 6. Implementation

### 6.1 SQL Operations

| Operation | Example |
|-----------|---------|
| **INSERT** | User registration, add usage, create bill, power report |
| **SELECT** | Dashboard data, filtered reports, analyst stats |
| **UPDATE** | Edit usage, mark report inspected/resolved |
| **DELETE** | Delete bill, appliance, tariff, usage |
| **Aggregation** | COUNT by status, COUNT by type |
| **Join** | usage + appliances for display |

### 6.2 Sample Queries (Application Logic)

**Get current tariff:**
```sql
SELECT rate_per_kwh FROM tariffs ORDER BY effective_date DESC LIMIT 1;
```

**User usage with appliance names (conceptual join):**
```sql
SELECT u.*, a.appliance_name, a.power_rating_watts
FROM usage u
JOIN appliances a ON u.appliance_id = a.id
WHERE u.user_id = ?;
```

**Power reports by status (analyst):**
```sql
SELECT status, COUNT(*) FROM power_reports GROUP BY status;
```

### 6.3 Key Routes

| Route | Method | Purpose |
|-------|--------|---------|
| / | GET | Home |
| /register | GET, POST | User registration |
| /login | GET, POST | Login (user/admin) |
| /platform | GET | User dashboard |
| /admin/dashboard | GET | Admin dashboard |
| /admin/data | GET | Database schema view |
| /admin/map/reports | GET | Power Analyst |
| /api/map/power-reports | GET | Map markers (JSON) |

---

## 7. Screenshots and Modules

### 7.1 Modules

1. **Home** — Landing page, Login, Register links
2. **User Dashboard** — Add usage, view records, bills, set budget
3. **Platform** — Usage, facilities, KSEB calculator
4. **Kerala Power Map** — Report outages, view markers
5. **Admin Dashboard** — Appliances, tariffs, bills, delete
6. **Power Analyst** — Stats, charts, filters, CSV export
7. **Database Schema** — Table counts, ER overview (/admin/data)

### 7.2 Screenshot Checklist (Add your own)

- [ ] Home page
- [ ] Login / Register
- [ ] User dashboard with usage
- [ ] Kerala Power Map
- [ ] Admin dashboard
- [ ] Power Analyst (stats, charts)
- [ ] Database Schema page

---

## 8. Conclusion

Smart Energy Platform successfully implements a relational database system for energy management. The schema is normalized (3NF), uses referential integrity, and supports full CRUD operations. The Power Analyst module demonstrates aggregation and export. The project is deployed at https://smart-energy-eykr.onrender.com and can be extended with authentication improvements, real-time notifications, and mobile support.

---

## 9. References

1. PostgreSQL Documentation — [postgresql.org/docs](https://www.postgresql.org/docs/)
2. Supabase — [supabase.com](https://supabase.com)
3. Flask — [flask.palletsprojects.com](https://flask.palletsprojects.com/)
4. KSEB — Kerala State Electricity Board tariff structure

---

## 10. Appendix

### A. Schema Files

- `supabase_schema.sql` — Full schema and seed data
- `supabase_migration_power_reports.sql` — power_reports table

### B. Setup Commands

```bash
pip install -r requirements.txt
# Add .env with SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SECRET_KEY
python3 dbms.py  # Runs on http://127.0.0.1:8000
```

### C. Default Credentials

- **Admin:** username `admin`, password `admin123`
- **User:** Register and login with email
