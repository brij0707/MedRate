import os
from supabase import create_client, Client

def test_supabase_connection():
    # Load secrets from GitHub environment
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ Error: Missing Supabase credentials in environment.")
        return

    try:
        # Initialize client
        supabase: Client = create_client(url, key)
        
        # Attempt a simple query
        response = supabase.table('colleges').select("count", count='exact').limit(1).execute()
        
        print("✅ Success! Successfully connected to Supabase.")
        print(f"📊 Current Colleges in database: {response.count}")
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    test_supabase_connection()
