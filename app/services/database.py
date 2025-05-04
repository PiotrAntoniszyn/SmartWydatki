import os
from supabase import create_client

# Singleton pattern for the Supabase client
_supabase_client = None

def get_supabase_client():
    """
    Get or create a Supabase client instance.
    Uses singleton pattern to avoid creating multiple clients.
    
    Returns:
        Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client 