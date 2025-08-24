import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import Dict, Tuple, List
import streamlit as st

class RiskAnalytics:
    """Comprehensive risk analytics calculations"""
    
    def __init__(self):
        pass
    
    def calculate_var(self, returns: pd.Series, confidence_levels: List[float] = [0.95, 0.99]) -> Dict[float, float]:
        """
        Calculate Value at Risk (VaR) using historical simulation
        
        Args:
            returns: Series of portfolio returns
            confidence_levels: List of confidence levels (e.g., [0.95, 0.99])
            
        Returns:
            Dictionary with VaR values for each confidence level
        """
        var_results = {}
        
        for confidence in confidence_levels:
            percentile = (1 - confidence) * 100
            var_value = np.percentile(returns, percentile)
            var_results[confidence] = var_value
            
        return var_results
    
    def calculate_cvar(self, returns: pd.Series, confidence_levels: List[float] = [0.95, 0.99]) -> Dict[float, float]:
        """
        Calculate Conditional Value at Risk (Expected Shortfall)
        
        Args:
            returns: Series of portfolio returns
            confidence_levels: List of confidence levels
            
        Returns:
            Dictionary with CVaR values for each confidence level
        """
        cvar_results = {}
        
        for confidence in confidence_levels:
            var_threshold = np.percentile(returns, (1 - confidence) * 100)
            tail_losses = returns[returns <= var_threshold]
            cvar_value = tail_losses.mean() if len(tail_losses) > 0 else var_threshold
            cvar_results[confidence] = cvar_value
            
        return cvar_results
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: Series of portfolio returns
            risk_free_rate: Risk-free rate (annual)
            
        Returns:
            Sharpe ratio
        """
        # Convert annual risk-free rate to daily
        daily_rf_rate = risk_free_rate / 252
        
        excess_returns = returns - daily_rf_rate
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std()
        
        # Annualize
        return sharpe * np.sqrt(252)
    
    def calculate_max_drawdown(self, prices: pd.Series) -> Dict[str, float]:
        """
        Calculate maximum drawdown
        
        Args:
            prices: Series of portfolio prices/values
            
        Returns:
            Dictionary with max drawdown metrics
        """
        # Calculate cumulative returns
        cumulative = (1 + prices.pct_change()).cumprod()
        
        # Calculate running maximum
        running_max = cumulative.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max
        
        max_drawdown = drawdown.min()
        
        # Find drawdown periods
        drawdown_start = None
        drawdown_end = None
        max_dd_start = None
        max_dd_end = None
        
        for i, dd in enumerate(drawdown):
            if dd < 0 and drawdown_start is None:
                drawdown_start = i
            elif dd == 0 and drawdown_start is not None:
                drawdown_end = i
                if dd == max_drawdown:
                    max_dd_start = drawdown_start
                    max_dd_end = drawdown_end
                drawdown_start = None
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_start': max_dd_start,
            'max_drawdown_end': max_dd_end,
            'drawdown_series': drawdown
        }
    
    def calculate_volatility(self, returns: pd.Series, annualize: bool = True) -> float:
        """
        Calculate volatility (standard deviation of returns)
        
        Args:
            returns: Series of returns
            annualize: Whether to annualize the volatility
            
        Returns:
            Volatility
        """
        vol = returns.std()
        
        if annualize:
            vol *= np.sqrt(252)  # Assuming daily data
            
        return vol
    
    def calculate_distribution_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """
        Calculate distribution metrics (skewness, kurtosis, etc.)
        
        Args:
            returns: Series of returns
            
        Returns:
            Dictionary with distribution metrics
        """
        return {
            'mean': returns.mean(),
            'std': returns.std(),
            'skewness': stats.skew(returns),
            'kurtosis': stats.kurtosis(returns),
            'min': returns.min(),
            'max': returns.max(),
            'jarque_bera_stat': stats.jarque_bera(returns)[0],
            'jarque_bera_pvalue': stats.jarque_bera(returns)[1]
        }
    
    def calculate_beta(self, stock_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate beta coefficient
        
        Args:
            stock_returns: Stock returns
            market_returns: Market/benchmark returns
            
        Returns:
            Beta coefficient
        """
        # Align the series
        aligned_data = pd.concat([stock_returns, market_returns], axis=1).dropna()
        
        if len(aligned_data) < 2:
            return 1.0
        
        stock_aligned = aligned_data.iloc[:, 0]
        market_aligned = aligned_data.iloc[:, 1]
        
        covariance = np.cov(stock_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return beta
    
    def calculate_tracking_error(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Calculate tracking error
        
        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Annualized tracking error
        """
        # Align the series
        aligned_data = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
        
        if len(aligned_data) < 2:
            return 0.0
        
        excess_returns = aligned_data.iloc[:, 0] - aligned_data.iloc[:, 1]
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        return tracking_error
    
    def calculate_information_ratio(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Calculate information ratio
        
        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Information ratio
        """
        # Align the series
        aligned_data = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
        
        if len(aligned_data) < 2:
            return 0.0
        
        excess_returns = aligned_data.iloc[:, 0] - aligned_data.iloc[:, 1]
        
        if excess_returns.std() == 0:
            return 0.0
        
        information_ratio = excess_returns.mean() / excess_returns.std()
        
        # Annualize
        return information_ratio * np.sqrt(252)
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02, target_return: float = 0) -> float:
        """
        Calculate Sortino ratio (downside deviation)
        
        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate
            target_return: Target return threshold
            
        Returns:
            Sortino ratio
        """
        daily_rf_rate = risk_free_rate / 252
        excess_returns = returns - daily_rf_rate
        
        # Calculate downside deviation
        downside_returns = excess_returns[excess_returns < target_return]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_deviation = np.sqrt(np.mean(downside_returns ** 2))
        
        if downside_deviation == 0:
            return float('inf')
        
        sortino = excess_returns.mean() / downside_deviation
        
        # Annualize
        return sortino * np.sqrt(252)
    
    def comprehensive_risk_report(self, returns: pd.Series, prices: pd.Series, 
                                 benchmark_returns: pd.Series = None, 
                                 risk_free_rate: float = 0.02) -> Dict:
        """
        Generate comprehensive risk analytics report
        
        Args:
            returns: Portfolio returns
            prices: Portfolio prices/values
            benchmark_returns: Benchmark returns (optional)
            risk_free_rate: Risk-free rate
            
        Returns:
            Dictionary with all risk metrics
        """
        report = {}
        
        # Basic metrics
        report['returns_mean'] = returns.mean() * 252  # Annualized
        report['returns_std'] = self.calculate_volatility(returns)
        
        # Risk metrics
        report['var'] = self.calculate_var(returns)
        report['cvar'] = self.calculate_cvar(returns)
        report['sharpe_ratio'] = self.calculate_sharpe_ratio(returns, risk_free_rate)
        report['sortino_ratio'] = self.calculate_sortino_ratio(returns, risk_free_rate)
        
        # Drawdown analysis
        drawdown_metrics = self.calculate_max_drawdown(prices)
        report['max_drawdown'] = drawdown_metrics['max_drawdown']
        report['drawdown_series'] = drawdown_metrics['drawdown_series']
        
        # Distribution metrics
        report['distribution'] = self.calculate_distribution_metrics(returns)
        
        # Benchmark comparison (if provided)
        if benchmark_returns is not None:
            report['beta'] = self.calculate_beta(returns, benchmark_returns)
            report['tracking_error'] = self.calculate_tracking_error(returns, benchmark_returns)
            report['information_ratio'] = self.calculate_information_ratio(returns, benchmark_returns)
        
        return report
