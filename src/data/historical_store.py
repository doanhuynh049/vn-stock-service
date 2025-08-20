"""
Local Data Storage System for Historical Portfolio Tracking
- SQLite database for storing daily snapshots
- Portfolio evolution tracking
- AI insights history
- Performance analytics
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PortfolioSnapshot:
    """Portfolio snapshot data structure"""
    snapshot_id: str
    date: str
    owner: str
    total_positions: int
    total_invested_value: float
    portfolio_data: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    advisory_mode: str
    created_at: str

@dataclass
class PerformanceMetrics:
    """Portfolio performance metrics"""
    date: str
    total_value: float
    daily_return: float
    cumulative_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    benchmark_return: float
    alpha: float
    beta: float

class HistoricalDataStore:
    """
    Local SQLite database for storing portfolio history and analysis
    """
    
    def __init__(self, db_path: str = "data/portfolio_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Portfolio snapshots table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                        snapshot_id TEXT PRIMARY KEY,
                        date TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        total_positions INTEGER,
                        total_invested_value REAL,
                        portfolio_data TEXT,
                        ai_analysis TEXT,
                        advisory_mode TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date, owner)
                    )
                ''')
                
                # Performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        total_value REAL,
                        daily_return REAL,
                        cumulative_return REAL,
                        volatility REAL,
                        sharpe_ratio REAL,
                        max_drawdown REAL,
                        benchmark_return REAL,
                        alpha REAL,
                        beta REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date, owner)
                    )
                ''')
                
                # AI insights table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ai_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        insight_type TEXT,
                        ticker TEXT,
                        recommendation TEXT,
                        rationale TEXT,
                        confidence_score REAL,
                        priority TEXT,
                        status TEXT DEFAULT 'active',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Position changes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS position_changes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        ticker TEXT NOT NULL,
                        change_type TEXT,
                        old_shares REAL,
                        new_shares REAL,
                        old_avg_price REAL,
                        new_avg_price REAL,
                        reason TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Configuration history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS config_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        config_type TEXT,
                        old_value TEXT,
                        new_value TEXT,
                        reason TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_date ON portfolio_snapshots(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_owner ON portfolio_snapshots(owner)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_insights_date ON ai_insights(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_insights_ticker ON ai_insights(ticker)')
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_portfolio_snapshot(self, portfolio_data: Dict[str, Any], 
                              ai_analysis: Dict[str, Any],
                              advisory_mode: str = "long_term") -> bool:
        """Save daily portfolio snapshot"""
        try:
            snapshot_id = f"{portfolio_data.get('owner', 'unknown')}_{datetime.now().strftime('%Y%m%d')}"
            date = datetime.now().strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO portfolio_snapshots 
                    (snapshot_id, date, owner, total_positions, total_invested_value, 
                     portfolio_data, ai_analysis, advisory_mode, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    snapshot_id,
                    date,
                    portfolio_data.get('owner', 'unknown'),
                    portfolio_data.get('total_positions', 0),
                    portfolio_data.get('total_invested_value', 0),
                    json.dumps(portfolio_data),
                    json.dumps(ai_analysis),
                    advisory_mode,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                logger.info(f"Saved portfolio snapshot for {date}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving portfolio snapshot: {e}")
            return False
    
    def save_ai_insights(self, insights: List[Dict[str, Any]], owner: str) -> bool:
        """Save AI insights and recommendations"""
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for insight in insights:
                    cursor.execute('''
                        INSERT INTO ai_insights 
                        (date, owner, insight_type, ticker, recommendation, 
                         rationale, confidence_score, priority, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        date,
                        owner,
                        insight.get('type', 'general'),
                        insight.get('ticker', ''),
                        insight.get('recommendation', ''),
                        insight.get('rationale', ''),
                        insight.get('confidence_score', 0.5),
                        insight.get('priority', 'medium'),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(insights)} AI insights for {date}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving AI insights: {e}")
            return False
    
    def get_portfolio_history(self, owner: str, days: int = 30) -> List[PortfolioSnapshot]:
        """Get portfolio history for specified period"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT snapshot_id, date, owner, total_positions, total_invested_value,
                           portfolio_data, ai_analysis, advisory_mode, created_at
                    FROM portfolio_snapshots
                    WHERE owner = ? AND date >= ?
                    ORDER BY date DESC
                ''', (owner, start_date))
                
                rows = cursor.fetchall()
                
                snapshots = []
                for row in rows:
                    snapshots.append(PortfolioSnapshot(
                        snapshot_id=row[0],
                        date=row[1],
                        owner=row[2],
                        total_positions=row[3],
                        total_invested_value=row[4],
                        portfolio_data=json.loads(row[5]) if row[5] else {},
                        ai_analysis=json.loads(row[6]) if row[6] else {},
                        advisory_mode=row[7],
                        created_at=row[8]
                    ))
                
                return snapshots
                
        except Exception as e:
            logger.error(f"Error getting portfolio history: {e}")
            return []
    
    def get_performance_evolution(self, owner: str, days: int = 90) -> pd.DataFrame:
        """Get portfolio performance evolution as DataFrame"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT date, total_value, daily_return, cumulative_return,
                           volatility, sharpe_ratio, max_drawdown, benchmark_return
                    FROM performance_metrics
                    WHERE owner = ? AND date >= ?
                    ORDER BY date
                '''
                
                df = pd.read_sql_query(query, conn, params=(owner, start_date))
                return df
                
        except Exception as e:
            logger.error(f"Error getting performance evolution: {e}")
            return pd.DataFrame()
    
    def calculate_portfolio_metrics(self, owner: str) -> Dict[str, Any]:
        """Calculate comprehensive portfolio metrics"""
        try:
            snapshots = self.get_portfolio_history(owner, days=365)
            
            if len(snapshots) < 2:
                return {"error": "Insufficient data for metrics calculation"}
            
            # Convert to DataFrame for easier analysis
            df_data = []
            for snapshot in snapshots:
                df_data.append({
                    'date': snapshot.date,
                    'total_value': snapshot.total_invested_value,
                    'positions': snapshot.total_positions
                })
            
            df = pd.DataFrame(df_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate returns
            df['daily_return'] = df['total_value'].pct_change()
            df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
            
            # Calculate risk metrics
            volatility = df['daily_return'].std() * (252 ** 0.5) if len(df) > 1 else 0
            mean_return = df['daily_return'].mean() * 252
            sharpe_ratio = mean_return / volatility if volatility > 0 else 0
            
            # Calculate max drawdown
            rolling_max = df['total_value'].expanding().max()
            drawdown = (df['total_value'] - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Current vs initial value
            initial_value = df['total_value'].iloc[0]
            current_value = df['total_value'].iloc[-1]
            total_return = (current_value - initial_value) / initial_value
            
            metrics = {
                'period_days': len(df),
                'initial_value': initial_value,
                'current_value': current_value,
                'total_return': total_return,
                'annualized_return': mean_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'best_day': df['daily_return'].max(),
                'worst_day': df['daily_return'].min(),
                'positive_days': (df['daily_return'] > 0).sum(),
                'negative_days': (df['daily_return'] < 0).sum(),
                'calculated_at': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {"error": f"Metrics calculation failed: {e}"}
    
    def get_ai_insights_history(self, owner: str, days: int = 30, 
                              ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical AI insights"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if ticker:
                    cursor.execute('''
                        SELECT date, insight_type, ticker, recommendation, rationale,
                               confidence_score, priority, status, created_at
                        FROM ai_insights
                        WHERE owner = ? AND date >= ? AND ticker = ?
                        ORDER BY created_at DESC
                    ''', (owner, start_date, ticker))
                else:
                    cursor.execute('''
                        SELECT date, insight_type, ticker, recommendation, rationale,
                               confidence_score, priority, status, created_at
                        FROM ai_insights
                        WHERE owner = ? AND date >= ?
                        ORDER BY created_at DESC
                    ''', (owner, start_date))
                
                rows = cursor.fetchall()
                
                insights = []
                for row in rows:
                    insights.append({
                        'date': row[0],
                        'insight_type': row[1],
                        'ticker': row[2],
                        'recommendation': row[3],
                        'rationale': row[4],
                        'confidence_score': row[5],
                        'priority': row[6],
                        'status': row[7],
                        'created_at': row[8]
                    })
                
                return insights
                
        except Exception as e:
            logger.error(f"Error getting AI insights history: {e}")
            return []
    
    def track_position_changes(self, owner: str, old_portfolio: Dict[str, Any], 
                             new_portfolio: Dict[str, Any], reason: str = "manual_update") -> bool:
        """Track changes in portfolio positions"""
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            
            # Create lookup dictionaries
            old_positions = {pos['ticker']: pos for pos in old_portfolio.get('positions', [])}
            new_positions = {pos['ticker']: pos for pos in new_portfolio.get('positions', [])}
            
            all_tickers = set(old_positions.keys()) | set(new_positions.keys())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for ticker in all_tickers:
                    old_pos = old_positions.get(ticker, {})
                    new_pos = new_positions.get(ticker, {})
                    
                    old_shares = old_pos.get('shares', 0)
                    new_shares = new_pos.get('shares', 0)
                    old_avg_price = old_pos.get('avg_price', 0)
                    new_avg_price = new_pos.get('avg_price', 0)
                    
                    # Determine change type
                    if old_shares == 0 and new_shares > 0:
                        change_type = "added"
                    elif old_shares > 0 and new_shares == 0:
                        change_type = "removed"
                    elif old_shares != new_shares:
                        change_type = "shares_changed"
                    elif old_avg_price != new_avg_price:
                        change_type = "price_updated"
                    else:
                        continue  # No change
                    
                    cursor.execute('''
                        INSERT INTO position_changes
                        (date, owner, ticker, change_type, old_shares, new_shares,
                         old_avg_price, new_avg_price, reason, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        date, owner, ticker, change_type,
                        old_shares, new_shares, old_avg_price, new_avg_price,
                        reason, datetime.now().isoformat()
                    ))
                
                conn.commit()
                logger.info(f"Tracked position changes for {date}")
                return True
                
        except Exception as e:
            logger.error(f"Error tracking position changes: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> bool:
        """Clean up old data beyond specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old snapshots
                cursor.execute('DELETE FROM portfolio_snapshots WHERE date < ?', (cutoff_date,))
                deleted_snapshots = cursor.rowcount
                
                # Clean up old performance metrics
                cursor.execute('DELETE FROM performance_metrics WHERE date < ?', (cutoff_date,))
                deleted_metrics = cursor.rowcount
                
                # Clean up old AI insights
                cursor.execute('DELETE FROM ai_insights WHERE date < ?', (cutoff_date,))
                deleted_insights = cursor.rowcount
                
                # Clean up old position changes
                cursor.execute('DELETE FROM position_changes WHERE date < ?', (cutoff_date,))
                deleted_changes = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Cleaned up old data: {deleted_snapshots} snapshots, "
                          f"{deleted_metrics} metrics, {deleted_insights} insights, "
                          f"{deleted_changes} position changes")
                
                return True
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
    
    def export_data(self, owner: str, export_path: str, 
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> bool:
        """Export portfolio data to CSV/JSON files"""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Set date range
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                # Export portfolio snapshots
                snapshots_query = '''
                    SELECT * FROM portfolio_snapshots 
                    WHERE owner = ? AND date BETWEEN ? AND ?
                    ORDER BY date
                '''
                df_snapshots = pd.read_sql_query(snapshots_query, conn, 
                                               params=(owner, start_date, end_date))
                df_snapshots.to_csv(export_dir / 'portfolio_snapshots.csv', index=False)
                
                # Export performance metrics
                metrics_query = '''
                    SELECT * FROM performance_metrics 
                    WHERE owner = ? AND date BETWEEN ? AND ?
                    ORDER BY date
                '''
                df_metrics = pd.read_sql_query(metrics_query, conn, 
                                             params=(owner, start_date, end_date))
                df_metrics.to_csv(export_dir / 'performance_metrics.csv', index=False)
                
                # Export AI insights
                insights_query = '''
                    SELECT * FROM ai_insights 
                    WHERE owner = ? AND date BETWEEN ? AND ?
                    ORDER BY created_at
                '''
                df_insights = pd.read_sql_query(insights_query, conn, 
                                              params=(owner, start_date, end_date))
                df_insights.to_csv(export_dir / 'ai_insights.csv', index=False)
                
                logger.info(f"Exported data to {export_dir}")
                return True
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

# Global instance
historical_store = HistoricalDataStore()
