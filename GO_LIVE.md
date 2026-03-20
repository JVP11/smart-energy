# Go Live – 3 Steps

## 1. Create GitHub repo (2 min)

1. Open **https://github.com/new**
2. Name: `smart-energy` → **Create repository**
3. Copy the repo URL (e.g. `https://github.com/johndoe/smart-energy.git`)

## 2. Push code

Run this (replace with YOUR repo URL):

```bash
cd /home/jonathan/jetson
git remote add origin https://github.com/YOUR_USERNAME/smart-energy.git
git push -u origin main
```

## 3. Deploy on Render (3 min)

1. Open **https://dashboard.render.com**
2. **New +** → **Web Service**
3. Select your `smart-energy` repo
4. Add env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SECRET_KEY`
5. **Create Web Service**
6. Wait ~3 min → your app is live

---

**Or** after pushing, open: **https://render.com/deploy** and select your repo.
