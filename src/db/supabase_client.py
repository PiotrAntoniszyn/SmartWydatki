import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 1) załaduj zmienne z .env (tylko jeśli używasz python-dotenv)
load_dotenv()

supabase_url: str = os.getenv("SUPABASE_URL") or ""
supabase_key: str = os.getenv("SUPABASE_KEY") or ""

if not supabase_url or not supabase_key:
    raise RuntimeError(
        "Brakuje zmiennych środowiskowych SUPABASE_URL lub SUPABASE_KEY"
    )

# 2) utwórz klienta
supabase: Client = create_client(supabase_url, supabase_key)