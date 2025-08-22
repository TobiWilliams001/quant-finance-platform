import numpy as np
import pandas as pd
import scipy.optimize as opt
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class PortfolioOptimizer:
    """Modern Portfolio Theory implementation for portfolio optimization"""
    
    def __init__(self, returns_data: pd.DataFrame, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer
        
        Args:
            returns_data: DataFrame with asset returns
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.returns = returns_data
        self.risk_free_rate = risk_free_rate
        self.mean_returns = returns_data.mean() * 252  # Annualized
        self.cov_matrix = returns_data.cov() * 252  # Annualized
        self.n_assets = len(returns_data.columns)
        
    def portfolio_performance(self, weights: np.array) -> Tuple[float, float, float]:
        """
        Calculate portfolio performance metrics
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Tuple of (expected_return, volatility, sharpe_ratio)
        """
        # Portfolio return
        portfolio_return = np.sum(self.mean_returns * weights)
        
        # Portfolio volatility
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        return portfolio_return, portfolio_std, sharpe_ratio
    
    def negative_sharpe(self, weights: np.array) -> float:
        """Negative Sharpe ratio for minimization"""
        return -self.portfolio_performance(weights)[2]
    
    def portfolio_volatility(self, weights: np.array) -> float:
        """Portfolio volatility for minimization"""
        return self.portfolio_performance(weights)[1]
    
    def optimize_sharpe(self) -> Dict:
        """
        Find portfolio with maximum Sharpe ratio
        
        Returns:
            Dictionary with optimization results
        """
        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Initial guess (equal weights)
        initial_guess = np.array([1/self.n_assets] * self.n_assets)
        
        # Optimization
        result = opt.minimize(
            self.negative_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        performance = self.portfolio_performance(optimal_weights)
        
        return {
            'weights': optimal_weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2],
            'success': result.success
        }
    
    def optimize_minimum_variance(self) -> Dict:
        """
        Find minimum variance portfolio
        
        Returns:
            Dictionary with optimization results
        """
        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Initial guess (equal weights)
        initial_guess = np.array([1/self.n_assets] * self.n_assets)
        
        # Optimization
        result = opt.minimize(
            self.portfolio_volatility,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        performance = self.portfolio_performance(optimal_weights)
        
        return {
            'weights': optimal_weights,
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2],
            'success': result.success
        }
    
    def efficient_frontier(self, num_portfolios: int = 100) -> Dict:
        """
        Generate efficient frontier
        
        Args:
            num_portfolios: Number of portfolios to generate
            
        Returns:
            Dictionary with frontier data
        """
        # Get min and max returns
        min_vol_portfolio = self.optimize_minimum_variance()
        max_sharpe_portfolio = self.optimize_sharpe()
        
        min_ret = min_vol_portfolio['expected_return']
        max_ret = self.mean_returns.max()
        
        # Target returns
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        frontier_volatility = []
        frontier_returns = []
        frontier_weights = []
        
        for target_return in target_returns:
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.sum(self.mean_returns * x) - target_return}
            ]
            bounds = tuple((0, 1) for _ in range(self.n_assets))
            
            # Initial guess
            initial_guess = np.array([1/self.n_assets] * self.n_assets)
            
            # Optimization
            result = opt.minimize(
                self.portfolio_volatility,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                weights = result.x
                ret, vol, sharpe = self.portfolio_performance(weights)
                
                frontier_returns.append(ret)
                frontier_volatility.append(vol)
                frontier_weights.append(weights)
        
        return {
            'returns': frontier_returns,
            'volatility': frontier_volatility,
            'weights': frontier_weights,
            'max_sharpe': max_sharpe_portfolio,
            'min_volatility': min_vol_portfolio
        }
    
    def plot_efficient_frontier(self, frontier_data: Dict) -> go.Figure:
        """
        Plot efficient frontier with optimal portfolios
        
        Args:
            frontier_data: Data from efficient_frontier method
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        # Efficient frontier
        fig.add_trace(go.Scatter(
            x=frontier_data['volatility'],
            y=frontier_data['returns'],
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='blue', width=3)
        ))
        
        # Maximum Sharpe ratio portfolio
        max_sharpe = frontier_data['max_sharpe']
        fig.add_trace(go.Scatter(
            x=[max_sharpe['volatility']],
            y=[max_sharpe['expected_return']],
            mode='markers',
            name=f'Max Sharpe Ratio ({max_sharpe["sharpe_ratio"]:.3f})',
            marker=dict(color='red', size=15, symbol='star')
        ))
        
        # Minimum volatility portfolio
        min_vol = frontier_data['min_volatility']
        fig.add_trace(go.Scatter(
            x=[min_vol['volatility']],
            y=[min_vol['expected_return']],
            mode='markers',
            name='Min Volatility',
            marker=dict(color='green', size=15, symbol='diamond')
        ))
        
        # Individual assets
        for asset in self.returns.columns:
            asset_return = self.mean_returns[asset]
            asset_vol = np.sqrt(self.cov_matrix.loc[asset, asset])
            
            fig.add_trace(go.Scatter(
                x=[asset_vol],
                y=[asset_return],
                mode='markers',
                name=asset,
                marker=dict(size=10)
            ))
        
        fig.update_layout(
            title='Efficient Frontier Analysis',
            xaxis_title='Volatility (Standard Deviation)',
            yaxis_title='Expected Return',
            hovermode='closest',
            showlegend=True
        )
        
        return fig
    
    def correlation_heatmap(self) -> go.Figure:
        """
        Create correlation heatmap
        
        Returns:
            Plotly figure
        """
        corr_matrix = self.returns.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 3),
            texttemplate='%{text}',
            textfont={'size': 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Asset Correlation Matrix',
            xaxis_title='Assets',
            yaxis_title='Assets'
        )
        
        return fig
    
    def portfolio_composition_pie(self, weights: np.array, labels: List[str]) -> go.Figure:
        """
        Create portfolio composition pie chart
        
        Args:
            weights: Portfolio weights
            labels: Asset labels
            
        Returns:
            Plotly figure
        """
        # Filter out zero weights
        non_zero_weights = weights[weights > 0.001]  # Threshold for display
        non_zero_labels = [labels[i] for i, w in enumerate(weights) if w > 0.001]
        
        fig = go.Figure(data=[go.Pie(
            labels=non_zero_labels,
            values=non_zero_weights,
            hole=0.3,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title='Portfolio Composition',
            showlegend=True
        )
        
        return fig
    
    def risk_return_scatter(self) -> go.Figure:
        """
        Create risk-return scatter plot for individual assets
        
        Returns:
            Plotly figure
        """
        returns = []
        volatilities = []
        sharpe_ratios = []
        
        for asset in self.returns.columns:
            asset_return = self.mean_returns[asset]
            asset_vol = np.sqrt(self.cov_matrix.loc[asset, asset])
            asset_sharpe = (asset_return - self.risk_free_rate) / asset_vol
            
            returns.append(asset_return)
            volatilities.append(asset_vol)
            sharpe_ratios.append(asset_sharpe)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=volatilities,
            y=returns,
            mode='markers+text',
            text=self.returns.columns,
            textposition='top center',
            marker=dict(
                size=15,
                color=sharpe_ratios,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            ),
            name='Assets'
        ))
        
        fig.update_layout(
            title='Risk-Return Analysis of Individual Assets',
            xaxis_title='Volatility (Standard Deviation)',
            yaxis_title='Expected Return',
            hovermode='closest'
        )
        
        return fig
