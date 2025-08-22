import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from statsmodels.tsa.stattools import coint, adfuller
from sklearn.linear_model import LinearRegression
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class PairsTrading:
    """Statistical arbitrage and pairs trading analysis"""
    
    def __init__(self):
        pass
    
    def cointegration_test(self, y: pd.Series, x: pd.Series) -> Dict:
        """
        Test for cointegration between two time series using Engle-Granger test
        
        Args:
            y: Dependent variable time series
            x: Independent variable time series
            
        Returns:
            Dictionary with cointegration test results
        """
        try:
            # Align the series
            aligned_data = pd.concat([y, x], axis=1).dropna()
            if len(aligned_data) < 20:
                return {'cointegrated': False, 'error': 'Insufficient data'}
            
            y_aligned = aligned_data.iloc[:, 0]
            x_aligned = aligned_data.iloc[:, 1]
            
            # Perform cointegration test
            coint_stat, p_value, critical_values = coint(y_aligned, x_aligned)
            
            # Check if cointegrated at 5% level
            is_cointegrated = p_value < 0.05
            
            return {
                'cointegrated': is_cointegrated,
                'test_statistic': coint_stat,
                'p_value': p_value,
                'critical_values': {
                    '1%': critical_values[0],
                    '5%': critical_values[1],
                    '10%': critical_values[2]
                },
                'y_series': y_aligned,
                'x_series': x_aligned
            }
            
        except Exception as e:
            return {'cointegrated': False, 'error': str(e)}
    
    def calculate_hedge_ratio(self, y: pd.Series, x: pd.Series) -> Dict:
        """
        Calculate hedge ratio using OLS regression
        
        Args:
            y: Dependent variable (stock to be hedged)
            x: Independent variable (hedging stock)
            
        Returns:
            Dictionary with regression results
        """
        try:
            # Align the series
            aligned_data = pd.concat([y, x], axis=1).dropna()
            if len(aligned_data) < 10:
                return {'error': 'Insufficient data for regression'}
            
            y_aligned = aligned_data.iloc[:, 0].values.reshape(-1, 1)
            x_aligned = aligned_data.iloc[:, 1].values.reshape(-1, 1)
            
            # Perform linear regression
            model = LinearRegression()
            model.fit(x_aligned, y_aligned)
            
            # Calculate statistics
            y_pred = model.predict(x_aligned)
            residuals = y_aligned.flatten() - y_pred.flatten()
            
            # R-squared
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((y_aligned.flatten() - np.mean(y_aligned)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Standard error
            n = len(residuals)
            mse = ss_res / (n - 2) if n > 2 else 0
            se_beta = np.sqrt(mse / np.sum((x_aligned.flatten() - np.mean(x_aligned)) ** 2)) if np.sum((x_aligned.flatten() - np.mean(x_aligned)) ** 2) != 0 else 0
            
            # t-statistic
            t_stat = model.coef_[0][0] / se_beta if se_beta != 0 else 0
            
            return {
                'hedge_ratio': model.coef_[0][0],
                'intercept': model.intercept_[0],
                'r_squared': r_squared,
                'residuals': residuals,
                'std_error': se_beta,
                't_statistic': t_stat,
                'y_aligned': aligned_data.iloc[:, 0],
                'x_aligned': aligned_data.iloc[:, 1]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_spread(self, y: pd.Series, x: pd.Series, hedge_ratio: float) -> pd.Series:
        """
        Calculate the spread between two assets
        
        Args:
            y: First asset prices
            x: Second asset prices
            hedge_ratio: Hedge ratio from regression
            
        Returns:
            Spread time series
        """
        aligned_data = pd.concat([y, x], axis=1).dropna()
        spread = aligned_data.iloc[:, 0] - hedge_ratio * aligned_data.iloc[:, 1]
        return spread
    
    def calculate_zscore(self, spread: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate rolling z-score of the spread
        
        Args:
            spread: Spread time series
            window: Rolling window for z-score calculation
            
        Returns:
            Z-score time series
        """
        rolling_mean = spread.rolling(window=window).mean()
        rolling_std = spread.rolling(window=window).std()
        
        zscore = (spread - rolling_mean) / rolling_std
        return zscore.dropna()
    
    def generate_trading_signals(self, zscore: pd.Series, entry_threshold: float = 2.0, 
                                exit_threshold: float = 0.5) -> Dict:
        """
        Generate trading signals based on z-score
        
        Args:
            zscore: Z-score time series
            entry_threshold: Z-score threshold for trade entry
            exit_threshold: Z-score threshold for trade exit
            
        Returns:
            Dictionary with trading signals and performance metrics
        """
        signals = pd.DataFrame(index=zscore.index)
        signals['zscore'] = zscore
        signals['long_signal'] = 0
        signals['short_signal'] = 0
        signals['position'] = 0
        
        # Generate signals
        for i in range(1, len(signals)):
            prev_zscore = signals['zscore'].iloc[i-1]
            curr_zscore = signals['zscore'].iloc[i]
            prev_position = signals['position'].iloc[i-1]
            
            # Entry signals
            if prev_position == 0:
                if curr_zscore > entry_threshold:
                    signals['short_signal'].iloc[i] = 1
                    signals['position'].iloc[i] = -1
                elif curr_zscore < -entry_threshold:
                    signals['long_signal'].iloc[i] = 1
                    signals['position'].iloc[i] = 1
                else:
                    signals['position'].iloc[i] = prev_position
            
            # Exit signals
            elif prev_position != 0:
                if abs(curr_zscore) < exit_threshold:
                    signals['position'].iloc[i] = 0
                else:
                    signals['position'].iloc[i] = prev_position
        
        # Calculate trade statistics
        position_changes = signals['position'].diff().fillna(0)
        n_trades = len(position_changes[position_changes != 0]) // 2
        
        # Calculate returns (simplified)
        signals['spread_returns'] = zscore.diff()
        signals['strategy_returns'] = signals['position'].shift(1) * signals['spread_returns'] * -1
        
        total_return = signals['strategy_returns'].sum()
        sharpe_ratio = signals['strategy_returns'].mean() / signals['strategy_returns'].std() * np.sqrt(252) if signals['strategy_returns'].std() != 0 else 0
        
        return {
            'signals': signals,
            'n_trades': n_trades,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': len(signals[signals['strategy_returns'] > 0]) / len(signals[signals['strategy_returns'] != 0]) if len(signals[signals['strategy_returns'] != 0]) > 0 else 0
        }
    
    def stationarity_test(self, series: pd.Series) -> Dict:
        """
        Test for stationarity using Augmented Dickey-Fuller test
        
        Args:
            series: Time series to test
            
        Returns:
            Dictionary with stationarity test results
        """
        try:
            # Perform ADF test
            adf_stat, p_value, used_lag, n_obs, critical_values, ic_best = adfuller(series.dropna())
            
            # Determine if stationary
            is_stationary = p_value < 0.05
            
            return {
                'is_stationary': is_stationary,
                'adf_statistic': adf_stat,
                'p_value': p_value,
                'critical_values': critical_values,
                'used_lag': used_lag,
                'n_observations': n_obs
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def plot_pairs_analysis(self, stock1_data: pd.Series, stock2_data: pd.Series, 
                           stock1_name: str, stock2_name: str) -> go.Figure:
        """
        Create comprehensive pairs trading analysis plot
        
        Args:
            stock1_data: First stock price data
            stock2_data: Second stock price data
            stock1_name: Name of first stock
            stock2_name: Name of second stock
            
        Returns:
            Plotly figure with multiple subplots
        """
        # Perform analysis
        coint_result = self.cointegration_test(stock1_data, stock2_data)
        
        if not coint_result.get('cointegrated', False):
            # Simple price comparison if not cointegrated
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=[f'{stock1_name} vs {stock2_name} Price Comparison', 'Correlation Analysis'],
                vertical_spacing=0.1
            )
            
            # Normalize prices for comparison
            norm_stock1 = stock1_data / stock1_data.iloc[0] * 100
            norm_stock2 = stock2_data / stock2_data.iloc[0] * 100
            
            fig.add_trace(go.Scatter(
                x=norm_stock1.index,
                y=norm_stock1.values,
                mode='lines',
                name=stock1_name,
                line=dict(color='blue')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=norm_stock2.index,
                y=norm_stock2.values,
                mode='lines',
                name=stock2_name,
                line=dict(color='red')
            ), row=1, col=1)
            
            # Scatter plot
            aligned_data = pd.concat([stock1_data, stock2_data], axis=1).dropna()
            if len(aligned_data) > 0:
                fig.add_trace(go.Scatter(
                    x=aligned_data.iloc[:, 1],
                    y=aligned_data.iloc[:, 0],
                    mode='markers',
                    name='Price Relationship',
                    marker=dict(size=5, opacity=0.6)
                ), row=2, col=1)
            
            fig.update_layout(
                title='Pairs Analysis (Not Cointegrated)',
                height=600
            )
            
            return fig
        
        # Full analysis for cointegrated pairs
        hedge_result = self.calculate_hedge_ratio(
            coint_result['y_series'], 
            coint_result['x_series']
        )
        
        if 'error' in hedge_result:
            return go.Figure().add_annotation(text="Error in hedge ratio calculation")
        
        spread = self.calculate_spread(
            coint_result['y_series'],
            coint_result['x_series'],
            hedge_result['hedge_ratio']
        )
        
        zscore = self.calculate_zscore(spread)
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=[
                f'Normalized Prices: {stock1_name} vs {stock2_name}',
                f'Hedge Ratio: {hedge_result["hedge_ratio"]:.4f} (R²: {hedge_result["r_squared"]:.3f})',
                'Spread Analysis',
                'Z-Score and Trading Signals'
            ],
            vertical_spacing=0.08,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Normalize prices for visualization
        y_norm = coint_result['y_series'] / coint_result['y_series'].iloc[0] * 100
        x_norm = coint_result['x_series'] / coint_result['x_series'].iloc[0] * 100
        
        # Plot 1: Normalized prices
        fig.add_trace(go.Scatter(
            x=y_norm.index,
            y=y_norm.values,
            mode='lines',
            name=stock1_name,
            line=dict(color='blue')
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=x_norm.index,
            y=x_norm.values,
            mode='lines',
            name=stock2_name,
            line=dict(color='red')
        ), row=1, col=1)
        
        # Plot 2: Regression scatter
        fig.add_trace(go.Scatter(
            x=hedge_result['x_aligned'],
            y=hedge_result['y_aligned'],
            mode='markers',
            name='Price Relationship',
            marker=dict(size=4, opacity=0.6, color='green'),
            showlegend=False
        ), row=2, col=1)
        
        # Add regression line
        x_range = np.linspace(hedge_result['x_aligned'].min(), hedge_result['x_aligned'].max(), 100)
        y_fitted = hedge_result['hedge_ratio'] * x_range + hedge_result['intercept']
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_fitted,
            mode='lines',
            name='Regression Line',
            line=dict(color='red', dash='dash'),
            showlegend=False
        ), row=2, col=1)
        
        # Plot 3: Spread
        fig.add_trace(go.Scatter(
            x=spread.index,
            y=spread.values,
            mode='lines',
            name='Spread',
            line=dict(color='purple'),
            showlegend=False
        ), row=3, col=1)
        
        # Add mean line
        fig.add_hline(
            y=spread.mean(),
            line_dash="dash",
            line_color="gray",
            row=3, col=1
        )
        
        # Plot 4: Z-Score
        fig.add_trace(go.Scatter(
            x=zscore.index,
            y=zscore.values,
            mode='lines',
            name='Z-Score',
            line=dict(color='orange'),
            showlegend=False
        ), row=4, col=1)
        
        # Add trading signal lines
        for threshold in [2, -2, 0.5, -0.5]:
            line_color = "red" if abs(threshold) == 2 else "green"
            line_dash = "solid" if abs(threshold) == 2 else "dash"
            
            fig.add_hline(
                y=threshold,
                line_dash=line_dash,
                line_color=line_color,
                row=4, col=1
            )
        
        fig.update_layout(
            title=f'Pairs Trading Analysis: {stock1_name} vs {stock2_name}',
            height=800,
            showlegend=True
        )
        
        # Update axis labels
        fig.update_yaxes(title_text="Normalized Price", row=1, col=1)
        fig.update_yaxes(title_text=f"{stock1_name} Price", row=2, col=1)
        fig.update_yaxes(title_text="Spread Value", row=3, col=1)
        fig.update_yaxes(title_text="Z-Score", row=4, col=1)
        fig.update_xaxes(title_text=f"{stock2_name} Price", row=2, col=1)
        
        return fig
    
    def pairs_summary_table(self, stock1_data: pd.Series, stock2_data: pd.Series) -> Dict:
        """
        Generate summary statistics for pairs analysis
        
        Args:
            stock1_data: First stock price data
            stock2_data: Second stock price data
            
        Returns:
            Dictionary with summary statistics
        """
        # Perform analysis
        coint_result = self.cointegration_test(stock1_data, stock2_data)
        
        summary = {
            'cointegration_p_value': coint_result.get('p_value', np.nan),
            'cointegrated': coint_result.get('cointegrated', False)
        }
        
        if coint_result.get('cointegrated', False):
            hedge_result = self.calculate_hedge_ratio(
                coint_result['y_series'], 
                coint_result['x_series']
            )
            
            if 'error' not in hedge_result:
                spread = self.calculate_spread(
                    coint_result['y_series'],
                    coint_result['x_series'],
                    hedge_result['hedge_ratio']
                )
                
                zscore = self.calculate_zscore(spread)
                signals = self.generate_trading_signals(zscore)
                
                # Test spread stationarity
                spread_stationarity = self.stationarity_test(spread)
                
                summary.update({
                    'hedge_ratio': hedge_result['hedge_ratio'],
                    'r_squared': hedge_result['r_squared'],
                    'spread_mean': spread.mean(),
                    'spread_std': spread.std(),
                    'spread_stationarity_p': spread_stationarity.get('p_value', np.nan),
                    'spread_is_stationary': spread_stationarity.get('is_stationary', False),
                    'avg_zscore': zscore.mean(),
                    'zscore_std': zscore.std(),
                    'n_trading_signals': signals['n_trades'],
                    'strategy_sharpe': signals['sharpe_ratio'],
                    'win_rate': signals['win_rate']
                })
        
        return summary
