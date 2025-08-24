import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st
from typing import Dict, List, Any, Optional
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class AnalysisHistory(Base):
    """Table to store analysis history"""
    __tablename__ = 'analysis_history'
    
    id = Column(Integer, primary_key=True)
    analysis_type = Column(String(50), nullable=False)  # 'risk', 'portfolio', 'options', 'monte_carlo', 'pairs'
    user_id = Column(String(100), default='anonymous')
    symbols = Column(Text)  # JSON string of symbols
    parameters = Column(Text)  # JSON string of parameters
    results = Column(Text)  # JSON string of results
    created_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    error_message = Column(Text)

class PortfolioSnapshots(Base):
    """Table to store portfolio snapshots"""
    __tablename__ = 'portfolio_snapshots'
    
    id = Column(Integer, primary_key=True)
    portfolio_name = Column(String(100), nullable=False)
    symbols = Column(Text)  # JSON string of symbols
    weights = Column(Text)  # JSON string of weights
    returns_data = Column(Text)  # JSON string of returns
    risk_metrics = Column(Text)  # JSON string of risk metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    benchmark = Column(String(10))
    period = Column(String(10))

class MarketDataCache(Base):
    """Table to cache market data"""
    __tablename__ = 'market_data_cache'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    period = Column(String(10), nullable=False)
    data_type = Column(String(20), default='price')  # 'price', 'returns', 'info'
    data = Column(Text)  # JSON string of data
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.initialized = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            # Get database URL from environment variables
            database_url = os.getenv('DATABASE_URL')
            
            if not database_url:
                logger.warning("No DATABASE_URL found. Database features will be disabled.")
                return
            
            # Create engine
            self.engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection established successfully")
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            self.initialized = False
    
    def create_tables(self):
        """Create all database tables"""
        if not self.initialized:
            logger.warning("Database not initialized. Cannot create tables.")
            return False
        
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            return False
    
    def get_session(self):
        """Get a database session"""
        if not self.initialized:
            return None
        return self.SessionLocal()
    
    def save_analysis_history(self, analysis_type: str, symbols: List[str], 
                            parameters: Dict, results: Dict, success: bool = True, 
                            error_message: str = None) -> bool:
        """Save analysis history to database"""
        if not self.initialized:
            return False
        
        try:
            session = self.get_session()
            
            history = AnalysisHistory(
                analysis_type=analysis_type,
                symbols=json.dumps(symbols),
                parameters=json.dumps(parameters, default=str),
                results=json.dumps(results, default=str),
                success=success,
                error_message=error_message
            )
            
            session.add(history)
            session.commit()
            session.close()
            
            logger.info(f"Analysis history saved: {analysis_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save analysis history: {str(e)}")
            return False
    
    def get_analysis_history(self, analysis_type: str = None, limit: int = 50) -> List[Dict]:
        """Retrieve analysis history from database"""
        if not self.initialized:
            return []
        
        try:
            session = self.get_session()
            
            query = session.query(AnalysisHistory)
            if analysis_type:
                query = query.filter(AnalysisHistory.analysis_type == analysis_type)
            
            history = query.order_by(AnalysisHistory.created_at.desc()).limit(limit).all()
            
            results = []
            for item in history:
                results.append({
                    'id': item.id,
                    'analysis_type': item.analysis_type,
                    'symbols': json.loads(item.symbols),
                    'parameters': json.loads(item.parameters),
                    'results': json.loads(item.results) if item.results else {},
                    'created_at': item.created_at,
                    'success': item.success,
                    'error_message': item.error_message
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve analysis history: {str(e)}")
            return []
    
    def save_portfolio_snapshot(self, portfolio_name: str, symbols: List[str], 
                              weights: Dict, returns_data: pd.DataFrame, 
                              risk_metrics: Dict, benchmark: str = None, 
                              period: str = None) -> bool:
        """Save portfolio snapshot to database"""
        if not self.initialized:
            return False
        
        try:
            session = self.get_session()
            
            # Convert DataFrame to JSON
            returns_json = returns_data.to_json(date_format='iso') if not returns_data.empty else "{}"
            
            snapshot = PortfolioSnapshots(
                portfolio_name=portfolio_name,
                symbols=json.dumps(symbols),
                weights=json.dumps(weights),
                returns_data=returns_json,
                risk_metrics=json.dumps(risk_metrics, default=str),
                benchmark=benchmark,
                period=period
            )
            
            session.add(snapshot)
            session.commit()
            session.close()
            
            logger.info(f"Portfolio snapshot saved: {portfolio_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save portfolio snapshot: {str(e)}")
            return False
    
    def get_portfolio_snapshots(self, limit: int = 20) -> List[Dict]:
        """Retrieve portfolio snapshots from database"""
        if not self.initialized:
            return []
        
        try:
            session = self.get_session()
            
            snapshots = session.query(PortfolioSnapshots)\
                             .order_by(PortfolioSnapshots.created_at.desc())\
                             .limit(limit).all()
            
            results = []
            for snapshot in snapshots:
                results.append({
                    'id': snapshot.id,
                    'portfolio_name': snapshot.portfolio_name,
                    'symbols': json.loads(snapshot.symbols),
                    'weights': json.loads(snapshot.weights),
                    'risk_metrics': json.loads(snapshot.risk_metrics) if snapshot.risk_metrics else {},
                    'created_at': snapshot.created_at,
                    'benchmark': snapshot.benchmark,
                    'period': snapshot.period
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve portfolio snapshots: {str(e)}")
            return []
    
    def cache_market_data(self, symbol: str, period: str, data: pd.DataFrame, 
                         data_type: str = 'price', expires_minutes: int = 60) -> bool:
        """Cache market data in database"""
        if not self.initialized:
            return False
        
        try:
            session = self.get_session()
            
            # Check if data already exists
            existing = session.query(MarketDataCache)\
                            .filter_by(symbol=symbol, period=period, data_type=data_type)\
                            .first()
            
            data_json = data.to_json(date_format='iso') if not data.empty else "{}"
            expires_at = datetime.utcnow().replace(microsecond=0) + pd.Timedelta(minutes=expires_minutes)
            
            if existing:
                # Update existing record
                existing.data = data_json
                existing.created_at = datetime.utcnow()
                existing.expires_at = expires_at
            else:
                # Create new record
                cache_entry = MarketDataCache(
                    symbol=symbol,
                    period=period,
                    data_type=data_type,
                    data=data_json,
                    expires_at=expires_at
                )
                session.add(cache_entry)
            
            session.commit()
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache market data: {str(e)}")
            return False
    
    def get_cached_market_data(self, symbol: str, period: str, 
                              data_type: str = 'price') -> Optional[pd.DataFrame]:
        """Retrieve cached market data"""
        if not self.initialized:
            return None
        
        try:
            session = self.get_session()
            
            cache_entry = session.query(MarketDataCache)\
                               .filter_by(symbol=symbol, period=period, data_type=data_type)\
                               .filter(MarketDataCache.expires_at > datetime.utcnow())\
                               .first()
            
            if cache_entry and cache_entry.data:
                data = pd.read_json(cache_entry.data, date_format='iso')
                session.close()
                logger.info(f"Retrieved cached data for {symbol} ({period})")
                return data
            
            session.close()
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached market data: {str(e)}")
            return None
    
    def cleanup_expired_cache(self) -> bool:
        """Remove expired cache entries"""
        if not self.initialized:
            return False
        
        try:
            session = self.get_session()
            
            expired_count = session.query(MarketDataCache)\
                                 .filter(MarketDataCache.expires_at < datetime.utcnow())\
                                 .delete()
            
            session.commit()
            session.close()
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        if not self.initialized:
            return {'status': 'disabled', 'message': 'Database not initialized'}
        
        try:
            session = self.get_session()
            
            stats = {}
            
            # Analysis history count
            stats['total_analyses'] = session.query(AnalysisHistory).count()
            stats['successful_analyses'] = session.query(AnalysisHistory)\
                                                 .filter(AnalysisHistory.success == True).count()
            
            # Portfolio snapshots count
            stats['total_portfolios'] = session.query(PortfolioSnapshots).count()
            
            # Cache statistics
            stats['cache_entries'] = session.query(MarketDataCache).count()
            stats['active_cache'] = session.query(MarketDataCache)\
                                          .filter(MarketDataCache.expires_at > datetime.utcnow())\
                                          .count()
            
            # Recent activity
            recent_analyses = session.query(AnalysisHistory)\
                                   .filter(AnalysisHistory.created_at >= datetime.utcnow() - pd.Timedelta(days=7))\
                                   .count()
            stats['recent_analyses_7d'] = recent_analyses
            
            session.close()
            
            stats['status'] = 'active'
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager

def initialize_database():
    """Initialize the database and create tables"""
    db_manager.create_tables()
    return db_manager.initialized