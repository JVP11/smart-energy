# Deploy to Render – Step by Step

Git is ready. Do these steps **in order**:

---

## Step 1: Create a GitHub repo

1. Go to **https://github.com/new**
2. Repository name: `smart-energy` (or any name)
3. Leave it **empty** (no README, no .gitignore)
4. Click **Create repository**

---

## Step 2: Push your code

Copy the URL of your new repo (e.g. `https://github.com/YOUR_USERNAME/smart-energy.git`), then run:

```bash
cd /home/jonathan/jetson
git remote add origin https://github.com/YOUR_USERNAME/smart-energy.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `smart-energy` with your actual GitHub username and repo name.

---

## Step 3: Deploy on Render

1. Go to **https://dashboard.render.com**
2. Click **New +** → **Web Service**
3. Connect GitHub if needed, then select your `smart-energy` repo
4. Use these settings:
   - **Name:** smart-energy-platform
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -b 0.0.0.0:${PORT:-10000} dbms:app`
5. Click **Advanced** → **Add Environment Variable** and add:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_SERVICE_ROLE_KEY` = your service_role key
   - `SECRET_KEY` = run `openssl rand -hex 32` and paste the result
6. Click **Create Web Service**
7. Wait 2–3 minutes for the build to finish

---

## Step 4: Open your app

When the build succeeds, Render will show a URL like:
`https://smart-energy-platform-xxxx.onrender.com`

Click it to open your app.
