# Deploy to Render

## Before you deploy

1. **Supabase** – Create a project at [supabase.com](https://supabase.com)
2. Run **supabase_schema.sql** in SQL Editor
3. Run **supabase_migration_power_reports.sql** if needed
4. Copy from **Settings → API**: Project URL and `service_role` key (use the JWT `eyJ...` one)

---

## Deploy steps

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Render Dashboard** → [dashboard.render.com](https://dashboard.render.com)
   - **New +** → **Web Service**
   - Connect **GitHub** → select `smart-energy` repo

3. **Settings** (Render will use `render.yaml` if present):
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn -b 0.0.0.0:$PORT dbms:app`

4. **Environment variables** → Add:
   | Key | Value |
   |----|-------|
   | `SUPABASE_URL` | `https://xxxx.supabase.co` |
   | `SUPABASE_SERVICE_ROLE_KEY` | `eyJ...` (service_role JWT) |
   | `SECRET_KEY` | `openssl rand -hex 32` |

5. **Create Web Service** → wait 2–3 min

6. **Open** the URL: `https://smart-energy-platform-xxxx.onrender.com`

---

## Troubleshooting

- **Build fails** – Check `requirements.txt` and Python 3.10+
- **500 on login/register** – Verify Supabase env vars, use JWT key not `sb_secret_`
- **Spins then times out** – Ensure `gunicorn` is in requirements.txt
