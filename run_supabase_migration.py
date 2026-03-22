#!/usr/bin/env python3
"""Run power_reports migration against Supabase. Requires DATABASE_URL in .env."""
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: Set DATABASE_URL in .env")
    print("Get it from: Supabase Dashboard → Project Settings → Database → Connection string (URI)")
    print("Format: postgresql://postgres.[ref]:[PASSWORD]@aws-0-xx.pooler.supabase.com:6543/postgres")
    exit(1)

# Support Render-style postgres:// → postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    import psycopg2
except ImportError:
    print("Installing psycopg2-binary...")
    import subprocess
    subprocess.check_call(["pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

MIGRATION_SQL = """
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
"""

def main():
    print("Connecting to Supabase...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    print("Running power_reports migration...")
    cur.execute(MIGRATION_SQL)
    cur.close()
    conn.close()
    print("OK: power_reports table created (or already exists)")

if __name__ == "__main__":
    main()
