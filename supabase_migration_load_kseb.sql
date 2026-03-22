-- Run in Supabase SQL Editor to store Load Calculation and KSEB estimate data

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
