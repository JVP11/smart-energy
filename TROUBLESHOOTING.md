# Troubleshooting

## 500 on Login or Register

**Possible causes:**

1. **Supabase key format** – New Supabase projects use `sb_secret_...` keys. If login fails:
   - Go to Supabase → Settings → API
   - Look for a **Legacy** or JWT-style `eyJ...` service_role key
   - Use that as `SUPABASE_SERVICE_ROLE_KEY` if the `sb_secret_` key fails

2. **Tables missing** – Run `supabase_schema.sql` in Supabase SQL Editor

3. **Wrong env vars** – Check Render Environment has all three:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SECRET_KEY`

## Health Check

Visit `https://your-app.onrender.com/health` to see the exact error:
- **OK** = Database connected
- Error message = Tells you what's wrong

## Admin Login

- Username: `admin`
- Password: `admin123`

(Seeded by `supabase_schema.sql` or `ensure_seed_data`)
