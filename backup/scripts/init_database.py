#!/usr/bin/env python3
"""
Database Initialization Script for Quantitative Finance Analytics Platform
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import initialize_database, get_db_manager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database for the quantitative finance platform"""
    
    print("🚀 Initializing Quantitative Finance Analytics Database")
    print("=" * 60)
    
    try:
        # Initialize database connection and create tables
        success = initialize_database()
        
        if success:
            print("✅ Database initialized successfully!")
            
            # Get database manager
            db_manager = get_db_manager()
            
            # Display database statistics
            stats = db_manager.get_database_stats()
            
            print("\n📊 Database Statistics:")
            print("-" * 30)
            print(f"Status: {stats.get('status', 'unknown')}")
            print(f"Total Analyses: {stats.get('total_analyses', 0)}")
            print(f"Portfolio Snapshots: {stats.get('total_portfolios', 0)}")
            print(f"Cache Entries: {stats.get('cache_entries', 0)}")
            
            # Cleanup expired cache entries
            db_manager.cleanup_expired_cache()
            
            print("\n🎯 Database Tables Created:")
            print("- analysis_history: Store analysis results and parameters")
            print("- portfolio_snapshots: Store portfolio configurations and metrics")
            print("- market_data_cache: Cache market data for improved performance")
            
            print("\n🔧 Next Steps:")
            print("1. Run the Streamlit application: streamlit run app.py")
            print("2. Database persistence will be automatically enabled")
            print("3. Check the admin panel for database statistics")
            
        else:
            print("❌ Failed to initialize database")
            print("Please check your DATABASE_URL environment variable")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()