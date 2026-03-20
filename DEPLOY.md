# Hosting Smart Energy Platform

## Quick deploy (Railway / Render / Fly.io)

1. **Supabase** – Create a project at [supabase.com](https://supabase.com), run `supabase_schema.sql`, get URL + service_role key.
2. **Push to GitHub** – Push this repo.
3. **Deploy** – Connect the repo to your platform.

### Environment variables

| Variable                     | Required | Description                                    |
|------------------------------|----------|------------------------------------------------|
| `SUPABASE_URL`               | Yes      | Supabase project URL (Settings → API)         |
| `SUPABASE_SERVICE_ROLE_KEY`  | Yes      | Service role key (Settings → API)             |
| `SECRET_KEY`                 | Yes      | Random string for session security             |
| `PORT`                       | Auto     | Set by platform (8080 default)                 |

### Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Add `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SECRET_KEY` in Variables
3. Deploy

### Render

1. Push your repo to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`. Or set manually:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn -b 0.0.0.0:$PORT dbms:app`
5. In **Environment** add:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_SERVICE_ROLE_KEY` = your service_role key
   - `SECRET_KEY` = random string (or let Render generate)
6. Click **Create Web Service**

### Fly.io

```bash
fly launch
fly secrets set SUPABASE_URL="https://xxx.supabase.co"
fly secrets set SUPABASE_SERVICE_ROLE_KEY="eyJ..."
fly secrets set SECRET_KEY="your-random-secret"
fly deploy
```

---

## Supabase setup (first-time)

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → New query → paste contents of `supabase_schema.sql` → Run
3. Go to **Settings → API** → copy Project URL and `service_role` key

## Self-hosted (VPS / your server)

```bash
pip install -r requirements.txt
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="eyJ..."
export SECRET_KEY="$(openssl rand -hex 32)"
gunicorn -b 0.0.0.0:8080 dbms:app
```

With **systemd** (`/etc/systemd/system/smart-energy.service`):

```ini
[Unit]
Description=Smart Energy Platform
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/jetson
Environment="SUPABASE_URL=https://xxx.supabase.co"
Environment="SUPABASE_SERVICE_ROLE_KEY=eyJ..."
Environment="SECRET_KEY=your-secret"
ExecStart=/usr/bin/gunicorn -b 0.0.0.0:8080 dbms:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then: `sudo systemctl enable --now smart-energy`

---

## Nginx reverse proxy (optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
