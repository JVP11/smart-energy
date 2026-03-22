-- Run in Supabase SQL Editor if power_reports table doesn't exist
-- (adds power reports for map: user "no current" + admin markers)

CREATE TABLE IF NOT EXISTS power_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lat NUMERIC NOT NULL,
  lng NUMERIC NOT NULL,
  report_type TEXT NOT NULL DEFAULT 'no_current',
  description TEXT DEFAULT '',
  status TEXT DEFAULT 'pending',
  reporter_type TEXT NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  admin_id UUID REFERENCES admins(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
