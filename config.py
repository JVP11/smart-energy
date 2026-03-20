import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY", "")

_supabase: Client | None = None


def get_db() -> Client:
    """Return Supabase client. Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY env vars."""
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError(
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) environment variables. "
                "Get them from Supabase Dashboard → Settings → API."
            )
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase
