import os
from dotenv import load_dotenv

# 1) Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

class Config:
    """Bazowa konfiguracja aplikacji Flask."""

    # — Sekretne klucze i sesje —
    # Wykorzystywane przez Flask do podpisywania ciasteczek sesji itp.
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    SESSION_PERMANENT = False

    # — Tryb pracy —
    # Ustawia tryb development/production, wykorzystywane np. przez debugtoolbar
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = ENV == "development"

    # — Klucze do zewnętrznych usług —
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    # (opcjonalnie) inne ustawienia, np. timeouty, limit JSON itp.
    # JSON_SORT_KEYS = False
    # PROPAGATE_EXCEPTIONS = True