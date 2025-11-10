#!/usr/bin/env python3
"""
Environment Configuration Verification Script

Verifies that all environment variables are properly loaded and configured.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_env_vars():
    """Verify all required environment variables are set"""
    
    print("="*70)
    print("ENVIRONMENT CONFIGURATION VERIFICATION")
    print("="*70)
    
    # Required variables
    required_vars = {
        'DB_HOST': 'Database host address',
        'DB_PORT': 'Database port',
        'DB_USER': 'Database username',
        'DB_PASSWORD': 'Database password',
        'DB_NAME': 'Database name',
    }
    
    # Optional variables
    optional_vars = {
        'DB_SSL_MODE': 'SSL connection mode',
        'API_HOST': 'API server host',
        'API_PORT': 'API server port',
    }
    
    print("\n📋 Required Variables:")
    print("-" * 70)
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask password
            if 'PASSWORD' in var:
                display_value = '*' * len(value)
            else:
                display_value = value
            status = "✅"
            print(f"{status} {var:20} = {display_value:30} ({description})")
        else:
            status = "❌"
            print(f"{status} {var:20} = {'NOT SET':30} ({description})")
            all_set = False
    
    print("\n📋 Optional Variables (with defaults):")
    print("-" * 70)
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            status = "✅"
            print(f"{status} {var:20} = {value:30} ({description})")
        else:
            status = "⚠️"
            print(f"{status} {var:20} = {'Using default':30} ({description})")
    
    print("\n" + "="*70)
    
    if all_set:
        print("✅ All required environment variables are set!")
        print("\n🔒 Security Check:")
        print("   - .env file should NOT be committed to git")
        print("   - .env file is in .gitignore: ", end="")
        
        # Check if .env is in .gitignore
        try:
            with open('../.gitignore', 'r') as f:
                gitignore_content = f.read()
                if '.env' in gitignore_content:
                    print("✅ Yes")
                else:
                    print("❌ No - Please add .env to .gitignore!")
        except FileNotFoundError:
            print("⚠️  .gitignore not found")
        
        print("\n🚀 Ready to start the API!")
        print("   Run: python main_db.py")
        
        return True
    else:
        print("❌ Some required environment variables are missing!")
        print("\n📝 Setup Instructions:")
        print("   1. Copy .env.example to .env:")
        print("      cp .env.example .env")
        print("   2. Edit .env with your database credentials")
        print("   3. Run this script again to verify")
        
        return False


def test_database_connection():
    """Test database connection with configured credentials"""
    
    print("\n" + "="*70)
    print("DATABASE CONNECTION TEST")
    print("="*70)
    
    try:
        from db_service import get_db_service
        
        print("\n🔌 Attempting to connect to database...")
        db_service = get_db_service()
        
        print("✅ Database connection successful!")
        
        # Get stats
        print("\n📊 Database Statistics:")
        stats = db_service.get_database_stats()
        print(f"   Total Traders: {stats['total_traders']}")
        print(f"   Non-Bot Traders: {stats['non_bot_traders']}")
        print(f"   Bot Traders: {stats['bot_traders']}")
        
        print("\n✅ Database is accessible and working!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify database credentials in .env")
        print("   2. Check network connectivity to database host")
        print("   3. Verify database port is accessible")
        print("   4. Try DB_SSL_MODE=DISABLED if SSL errors occur")
        return False


if __name__ == "__main__":
    # Verify environment variables
    env_ok = verify_env_vars()
    
    # Test database connection if env vars are set
    if env_ok:
        test_database_connection()
    
    print("\n" + "="*70)
    print("For more information, see: CONFIG.md")
    print("="*70)
