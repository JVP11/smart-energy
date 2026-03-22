-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New query)
-- Smart Energy Platform schema for Supabase

-- Admins (admin login)
CREATE TABLE IF NOT EXISTS admins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Users (consumer registration)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  monthly_budget NUMERIC DEFAULT 0
);

-- Appliances (catalog)
CREATE TABLE IF NOT EXISTS appliances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  appliance_name TEXT NOT NULL,
  power_rating_watts INTEGER NOT NULL
);

-- Usage (user appliance usage)
CREATE TABLE IF NOT EXISTS usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  appliance_id UUID NOT NULL REFERENCES appliances(id),
  hours_per_day INTEGER NOT NULL,
  number_of_days INTEGER NOT NULL
);

-- Tariffs
CREATE TABLE IF NOT EXISTS tariffs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rate_per_kwh NUMERIC NOT NULL,
  effective_date DATE NOT NULL
);

-- Bills
CREATE TABLE IF NOT EXISTS bills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  total_units NUMERIC NOT NULL,
  total_cost NUMERIC NOT NULL,
  bill_date DATE NOT NULL
);

-- Facilities
CREATE TABLE IF NOT EXISTS facilities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type TEXT DEFAULT 'Building',
  zone TEXT DEFAULT ''
);

-- Seed admin (username: admin, password: admin123)
INSERT INTO admins (username, password) VALUES ('admin', 'admin123')
ON CONFLICT (username) DO NOTHING;

-- Seed default tariff
INSERT INTO tariffs (rate_per_kwh, effective_date)
SELECT 8.0, CURRENT_DATE
WHERE NOT EXISTS (SELECT 1 FROM tariffs LIMIT 1);

-- Power reports: user "no current" reports + admin infrastructure markers (shown on map)
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

-- report_type: no_current, fluctuating, line_damaged, pole_down (user); ok, issue, maintenance (admin)
-- status: pending, inspected, resolved

-- Load calculations: NEC-style panel sizing (saved when user calculates)
CREATE TABLE IF NOT EXISTS load_calculations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  connected_load_watts NUMERIC NOT NULL,
  demand_factor NUMERIC NOT NULL,
  voltage NUMERIC NOT NULL,
  demand_load_watts NUMERIC NOT NULL,
  suggested_amps NUMERIC NOT NULL,
  panel_size_amps INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- KSEB estimates: saved when user clicks "Save estimate"
CREATE TABLE IF NOT EXISTS kseb_estimates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  units NUMERIC NOT NULL,
  energy_charge NUMERIC NOT NULL,
  fixed_charge NUMERIC NOT NULL,
  fuel_surcharge NUMERIC NOT NULL,
  electricity_duty NUMERIC NOT NULL,
  total NUMERIC NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Seed appliances (only if table is empty)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM appliances LIMIT 1) THEN
    INSERT INTO appliances (appliance_name, power_rating_watts) VALUES
      ('LED Bulb 9W', 9), ('LED Tube Light 20W', 20), ('Ceiling Fan', 60),
      ('Refrigerator 190L', 180), ('Refrigerator 300L', 250),
      ('1 Ton Inverter AC', 1200), ('1.5 Ton Inverter AC', 1500),
      ('Washing Machine (Front Load)', 500), ('LED TV 32"', 60),
      ('LED TV 43"', 90), ('Laptop Charger', 65), ('Desktop PC', 200),
      ('Water Heater (Geyser)', 2000), ('Mixer Grinder', 750),
      ('Electric Iron', 1000);
  END IF;
END $$;
