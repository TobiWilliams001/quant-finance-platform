import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Tuple, List
import streamlit as st

class BlackScholesModel:
    """Black-Scholes options pricing model implementation"""
    
    def __init__(self):
        pass
    
    def black_scholes_price(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> float:
        """
        Calculate Black-Scholes option price
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Option price
        """
        if T <= 0:
            if option_type == 'call':
                return max(S - K, 0)
            else:
                return max(K - S, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:  # put
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        return price
    
    def calculate_greeks(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> Dict[str, float]:
        """
        Calculate all Greeks for an option
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Dictionary with all Greeks
        """
        if T <= 0:
            return {
                'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0
            }
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Delta
        if option_type == 'call':
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1
        
        # Gamma (same for calls and puts)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        
        # Theta
        if option_type == 'call':
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        else:
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                    + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
        # Vega (same for calls and puts)
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        
        # Rho
        if option_type == 'call':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
    
    def implied_volatility(self, market_price: float, S: float, K: float, T: float, r: float, option_type: str = 'call') -> float:
        """
        Calculate implied volatility using Brent's method
        
        Args:
            market_price: Observed market price of the option
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            Implied volatility
        """
        def objective(sigma):
            try:
                price = self.black_scholes_price(S, K, T, r, sigma, option_type)
                return abs(price - market_price)
            except:
                return float('inf')
        
        try:
            result = minimize_scalar(objective, bounds=(0.001, 5.0), method='bounded')
            return result.x if result.success else 0.20  # Default 20% if optimization fails
        except:
            return 0.20
    
    def option_payoff(self, spot_prices: np.array, K: float, option_type: str = 'call') -> np.array:
        """
        Calculate option payoff at expiration
        
        Args:
            spot_prices: Array of underlying asset prices
            K: Strike price
            option_type: 'call' or 'put'
            
        Returns:
            Array of payoffs
        """
        if option_type == 'call':
            return np.maximum(spot_prices - K, 0)
        else:
            return np.maximum(K - spot_prices, 0)
    
    def plot_option_payoff(self, S: float, K: float, option_type: str = 'call') -> go.Figure:
        """
        Plot option payoff diagram
        
        Args:
            S: Current stock price
            K: Strike price
            option_type: 'call' or 'put'
            
        Returns:
            Plotly figure
        """
        # Create range of stock prices
        price_range = np.linspace(S * 0.5, S * 1.5, 100)
        payoffs = self.option_payoff(price_range, K, option_type)
        
        fig = go.Figure()
        
        # Payoff line
        fig.add_trace(go.Scatter(
            x=price_range,
            y=payoffs,
            mode='lines',
            name=f'{option_type.capitalize()} Payoff',
            line=dict(color='blue', width=3)
        ))
        
        # Strike price line
        fig.add_vline(
            x=K,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Strike: ${K:.2f}"
        )
        
        # Current price line
        fig.add_vline(
            x=S,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Current: ${S:.2f}"
        )
        
        fig.update_layout(
            title=f'{option_type.capitalize()} Option Payoff Diagram',
            xaxis_title='Underlying Asset Price ($)',
            yaxis_title='Payoff ($)',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_greeks_sensitivity(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> go.Figure:
        """
        Plot Greeks sensitivity analysis
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Plotly figure with subplots for each Greek
        """
        # Create price range
        price_range = np.linspace(S * 0.7, S * 1.3, 50)
        
        deltas = []
        gammas = []
        vegas = []
        thetas = []
        
        for price in price_range:
            greeks = self.calculate_greeks(price, K, T, r, sigma, option_type)
            deltas.append(greeks['delta'])
            gammas.append(greeks['gamma'])
            vegas.append(greeks['vega'])
            thetas.append(greeks['theta'])
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Delta', 'Gamma', 'Vega', 'Theta'),
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # Delta
        fig.add_trace(go.Scatter(
            x=price_range, y=deltas,
            mode='lines', name='Delta',
            line=dict(color='blue')
        ), row=1, col=1)
        
        # Gamma
        fig.add_trace(go.Scatter(
            x=price_range, y=gammas,
            mode='lines', name='Gamma',
            line=dict(color='red')
        ), row=1, col=2)
        
        # Vega
        fig.add_trace(go.Scatter(
            x=price_range, y=vegas,
            mode='lines', name='Vega',
            line=dict(color='green')
        ), row=2, col=1)
        
        # Theta
        fig.add_trace(go.Scatter(
            x=price_range, y=thetas,
            mode='lines', name='Theta',
            line=dict(color='orange')
        ), row=2, col=2)
        
        # Add current price lines
        for row in [1, 1, 2, 2]:
            for col in [1, 2, 1, 2]:
                fig.add_vline(x=S, line_dash="dash", line_color="gray", row=row, col=col)
        
        fig.update_layout(
            title=f'{option_type.capitalize()} Option Greeks Sensitivity',
            showlegend=False,
            height=600
        )
        
        # Update x-axis labels
        fig.update_xaxes(title_text="Underlying Price ($)")
        
        return fig
    
    def time_decay_analysis(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> go.Figure:
        """
        Analyze option price decay over time
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Plotly figure showing time decay
        """
        # Create time range (from current time to expiration)
        time_range = np.linspace(T, 0, 100)
        
        prices = []
        thetas = []
        
        for time_left in time_range:
            if time_left > 0:
                price = self.black_scholes_price(S, K, time_left, r, sigma, option_type)
                greeks = self.calculate_greeks(S, K, time_left, r, sigma, option_type)
                theta = greeks['theta']
            else:
                # At expiration
                if option_type == 'call':
                    price = max(S - K, 0)
                else:
                    price = max(K - S, 0)
                theta = 0
            
            prices.append(price)
            thetas.append(theta)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Option Price Over Time', 'Theta (Time Decay)'),
            vertical_spacing=0.15
        )
        
        # Option price
        fig.add_trace(go.Scatter(
            x=time_range * 365,  # Convert to days
            y=prices,
            mode='lines',
            name='Option Price',
            line=dict(color='blue', width=3)
        ), row=1, col=1)
        
        # Theta
        fig.add_trace(go.Scatter(
            x=time_range * 365,  # Convert to days
            y=thetas,
            mode='lines',
            name='Theta',
            line=dict(color='red', width=3)
        ), row=2, col=1)
        
        fig.update_layout(
            title=f'{option_type.capitalize()} Option Time Decay Analysis',
            showlegend=False,
            height=600
        )
        
        fig.update_xaxes(title_text="Days to Expiration", row=2, col=1)
        fig.update_yaxes(title_text="Option Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Theta ($/day)", row=2, col=1)
        
        return fig
    
    def volatility_surface_analysis(self, S: float, K_range: List[float], T_range: List[float], 
                                  r: float, sigma: float, option_type: str = 'call') -> go.Figure:
        """
        Create volatility surface analysis
        
        Args:
            S: Current stock price
            K_range: Range of strike prices
            T_range: Range of times to expiration
            r: Risk-free rate
            sigma: Base volatility
            option_type: 'call' or 'put'
            
        Returns:
            3D surface plot
        """
        K_grid, T_grid = np.meshgrid(K_range, T_range)
        prices = np.zeros_like(K_grid)
        
        for i, T in enumerate(T_range):
            for j, K in enumerate(K_range):
                prices[i, j] = self.black_scholes_price(S, K, T, r, sigma, option_type)
        
        fig = go.Figure(data=[go.Surface(
            z=prices,
            x=K_grid,
            y=T_grid,
            colorscale='Viridis',
            colorbar=dict(title="Option Price ($)")
        )])
        
        fig.update_layout(
            title=f'{option_type.capitalize()} Option Price Surface',
            scene=dict(
                xaxis_title='Strike Price ($)',
                yaxis_title='Time to Expiration (Years)',
                zaxis_title='Option Price ($)'
            ),
            height=600
        )
        
        return fig
