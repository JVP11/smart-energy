# Smart Energy Platform

**Industrial Power & Energy Management**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Overview

Enterprise-grade platform combining:

- **Load Calculation** — NEC compliance, panel & cable sizing (PowerCalc, Elek, Kopperfield equivalent)
- **Infrastructure** — Power grids, microgrids, substations (ETAP, Electrisim, nPro)
- **Energy Modeling** — Consumption analysis & trends (IESVE, DesignBuilder, eQUEST)
- **Facility Management** — Real-time monitoring & alerts (EcoStruxure, BuildTrack)

## Setup (local)

1. `pip install -r requirements.txt`
2. Add `.env` with `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SECRET_KEY`
3. Run `supabase_schema.sql` in Supabase SQL Editor
4. `python3 dbms.py`
5. Open http://127.0.0.1:8080

## Login

- **Admin:** `admin` / `admin123`
- **User:** Register, then login with email
