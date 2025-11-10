"""
Database Service for Trader Analysis API

Handles all database interactions and data retrieval for trader analysis.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import pandas as pd
from typing import Optional, List, Dict, Any
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for managing database connections and queries"""
    
    # Database configuration from environment variables
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'ssl_mode': os.getenv('DB_SSL_MODE')
    }
    
    def __init__(self):
        """Initialize database service with connection pool"""
        self.engine = None
        self._connect()
    
    def _connect(self):
        """Establish database connection with SSL disabled"""
        try:
            # Create connection URL
            db_url = (
                f"mysql+pymysql://{self.DB_CONFIG['user']}:{self.DB_CONFIG['password']}"
                f"@{self.DB_CONFIG['host']}:{self.DB_CONFIG['port']}/{self.DB_CONFIG['database']}"
            )
            
            # Determine SSL configuration
            ssl_config = {'ssl_mode': self.DB_CONFIG['ssl_mode']}
            
            # Create engine with connection pooling and SSL configuration
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                connect_args={
                    'ssl': ssl_config
                }
            )
            
            logger.info(f"Database connection established successfully to {self.DB_CONFIG['host']}")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_all_traders(self, exclude_bots: bool = True) -> pd.DataFrame:
        """
        Retrieve all traders from database
        
        Parameters:
        -----------
        exclude_bots : bool
            If True, filter out bot accounts
            
        Returns:
        --------
        pd.DataFrame
            DataFrame containing all trader data
        """
        try:
            query = "SELECT * FROM traders"
            if exclude_bots:
                query += " WHERE is_bot = 0"
            
            df = pd.read_sql(query, self.engine)
            logger.info(f"Retrieved {len(df)} traders from database")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving traders: {e}")
            raise
    
    def get_trader_by_address(self, wallet_address: str) -> Optional[pd.Series]:
        """
        Retrieve specific trader by wallet address
        
        Parameters:
        -----------
        wallet_address : str
            Trader's wallet address
            
        Returns:
        --------
        pd.Series or None
            Trader data or None if not found
        """
        try:
            query = text("SELECT * FROM traders WHERE wallet_address = :address")
            df = pd.read_sql(query, self.engine, params={'address': wallet_address})
            
            if len(df) == 0:
                return None
            
            return df.iloc[0]
            
        except Exception as e:
            logger.error(f"Error retrieving trader {wallet_address}: {e}")
            raise
    
    def get_top_traders(
        self, 
        limit: int = 50, 
        sort_by: str = 'realized_profit',
        exclude_bots: bool = True
    ) -> pd.DataFrame:
        """
        Retrieve top traders sorted by specified metric
        
        Parameters:
        -----------
        limit : int
            Number of traders to return
        sort_by : str
            Column to sort by
        exclude_bots : bool
            If True, filter out bot accounts
            
        Returns:
        --------
        pd.DataFrame
            DataFrame containing top traders
        """
        try:
            # Validate sort_by column
            valid_columns = [
                'gross_profit', 'realized_profit', 'win_rate', 
                'trade_volume', 'trades', 'realized_profit_percent'
            ]
            
            if sort_by not in valid_columns:
                sort_by = 'realized_profit'
            
            query = f"SELECT * FROM traders"
            if exclude_bots:
                query += " WHERE is_bot = 0"
            query += f" ORDER BY {sort_by} DESC LIMIT {limit}"
            
            df = pd.read_sql(query, self.engine)
            logger.info(f"Retrieved top {len(df)} traders sorted by {sort_by}")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving top traders: {e}")
            raise
    
    def get_traders_by_filter(
        self,
        min_win_rate: Optional[float] = None,
        min_trades: Optional[int] = None,
        min_volume: Optional[float] = None,
        min_profit: Optional[float] = None,
        exclude_bots: bool = True
    ) -> pd.DataFrame:
        """
        Retrieve traders matching specified filters
        
        Parameters:
        -----------
        min_win_rate : float, optional
            Minimum win rate percentage
        min_trades : int, optional
            Minimum number of trades
        min_volume : float, optional
            Minimum trade volume
        min_profit : float, optional
            Minimum realized profit
        exclude_bots : bool
            If True, filter out bot accounts
            
        Returns:
        --------
        pd.DataFrame
            DataFrame containing filtered traders
        """
        try:
            conditions = []
            
            if exclude_bots:
                conditions.append("is_bot = 0")
            
            if min_win_rate is not None:
                conditions.append(f"win_rate >= {min_win_rate}")
            
            if min_trades is not None:
                conditions.append(f"trades >= {min_trades}")
            
            if min_volume is not None:
                conditions.append(f"trade_volume >= {min_volume}")
            
            if min_profit is not None:
                conditions.append(f"realized_profit >= {min_profit}")
            
            query = "SELECT * FROM traders"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            df = pd.read_sql(query, self.engine)
            logger.info(f"Retrieved {len(df)} traders matching filters")
            return df
            
        except Exception as e:
            logger.error(f"Error filtering traders: {e}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get overall database statistics
        
        Returns:
        --------
        dict
            Statistics about the database
        """
        try:
            stats = {}
            
            # Total traders
            query = "SELECT COUNT(*) as total FROM traders"
            result = pd.read_sql(query, self.engine)
            stats['total_traders'] = int(result.iloc[0]['total'])
            
            # Non-bot traders
            query = "SELECT COUNT(*) as total FROM traders WHERE is_bot = 0"
            result = pd.read_sql(query, self.engine)
            stats['non_bot_traders'] = int(result.iloc[0]['total'])
            
            # Bot traders
            stats['bot_traders'] = stats['total_traders'] - stats['non_bot_traders']
            
            # Average statistics (non-bots only)
            query = """
                SELECT 
                    AVG(win_rate) as avg_win_rate,
                    AVG(trades) as avg_trades,
                    AVG(trade_volume) as avg_volume,
                    AVG(realized_profit) as avg_profit,
                    SUM(realized_profit) as total_profit,
                    SUM(trade_volume) as total_volume
                FROM traders 
                WHERE is_bot = 0
            """
            result = pd.read_sql(query, self.engine)
            
            stats['avg_win_rate'] = float(result.iloc[0]['avg_win_rate'] or 0)
            stats['avg_trades'] = float(result.iloc[0]['avg_trades'] or 0)
            stats['avg_volume'] = float(result.iloc[0]['avg_volume'] or 0)
            stats['avg_profit'] = float(result.iloc[0]['avg_profit'] or 0)
            stats['total_profit'] = float(result.iloc[0]['total_profit'] or 0)
            stats['total_volume'] = float(result.iloc[0]['total_volume'] or 0)
            
            logger.info("Retrieved database statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving database stats: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Singleton instance
_db_service = None

def get_db_service() -> DatabaseService:
    """Get or create database service singleton"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
