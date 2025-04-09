#!/usr/bin/env python
"""
Domo Connection Test Script
This script tests the connection to Domo using credentials from the .env file.
It attempts to connect to both the SQL warehouse and the Domo API.
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get Domo credentials from environment variables
DOMO_HOST = os.getenv("DOMO_HOST")
DOMO_DEVELOPER_TOKEN = os.getenv("DOMO_DEVELOPER_TOKEN")

def check_env_vars():
    """Check if all required environment variables are set"""
    missing = []
    if not DOMO_HOST:
        missing.append("DOMO_HOST")
    if not DOMO_DEVELOPER_TOKEN:
        missing.append("DOMO_DEVELOPER_TOKEN")
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease check your .env file and make sure all required variables are set.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_domo_api():
    """Test connection to Domo API"""
    import requests
    
    print("\nTesting Domo API connection...")
    
    try:
        headers = {
            "X-DOMO-Developer-Token": DOMO_DEVELOPER_TOKEN,
            "Content-Type": "application/json"
        }
        
        url = f"https://{DOMO_HOST}/api/content/v2/groups/grouplist?limit=1"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Successfully connected to Domo API")
            return True
        else:
            print(f"❌ Failed to connect to Domo API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Domo API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Databricks Connection Test")
    print("=========================\n")
    
    # Check for dependencies
    try:
        import requests
    except ImportError as e:
        print(f"❌ Missing dependency: {str(e)}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run tests
    env_ok = check_env_vars()
    
    if not env_ok:
        sys.exit(1)
    
    api_ok = test_domo_api()
    
    # Summary
    print("\nTest Summary")
    print("===========")
    print(f"Environment Variables: {'✅ OK' if env_ok else '❌ Failed'}")
    print(f"Domo API: {'✅ OK' if api_ok else '❌ Failed'}")
    
    if env_ok and api_ok:
        print("\n✅ All tests passed! Your Domo MCP server should work correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above and fix your configuration.")
        sys.exit(1) 