from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from scipy import stats


class MonteCarloSimulation:
    """Monte Carlo simulation for financial modeling"""

    def __init__(self):
        pass

    def geometric_brownian_motion(
        self,
        S0: float,
        mu: float,
        sigma: float,
        T: float,
        dt: float,
        n_simulations: int = 1000,
        random_seed: Optional[int] = None,
    ) -> np.ndarray:
        """
        Simulate stock price paths using Geometric Brownian Motion

        Args:
            S0: Initial stock price
            mu: Expected return (drift)
            sigma: Volatility
            T: Time horizon
            dt: Time step
            n_simulations: Number of simulation paths

        Returns:
            Array of simulated price paths
        """
        n_steps = int(T / dt)

        # Initialize price array
        prices = np.zeros((n_simulations, n_steps + 1))
        prices[:, 0] = S0

        # Generate random shocks
        rng = np.random.default_rng(random_seed)
        random_shocks = rng.normal(0, 1, (n_simulations, n_steps))

        # Simulate price paths
        for t in range(1, n_steps + 1):
            prices[:, t] = prices[:, t - 1] * np.exp(
                (mu - 0.5 * sigma**2) * dt
                + sigma * np.sqrt(dt) * random_shocks[:, t - 1]
            )

        return prices

    def jump_diffusion_simulation(
        self,
        S0: float,
        mu: float,
        sigma: float,
        jump_intensity: float,
        jump_mean: float,
        jump_std: float,
        T: float,
        dt: float,
        n_simulations: int = 1000,
        random_seed: Optional[int] = None,
    ) -> np.ndarray:
        """
        Simulate stock prices with jump diffusion (Merton model)

        Args:
            S0: Initial stock price
            mu: Expected return
            sigma: Volatility
            jump_intensity: Jump frequency (lambda)
            jump_mean: Mean jump size
            jump_std: Jump size standard deviation
            T: Time horizon
            dt: Time step
            n_simulations: Number of simulations

        Returns:
            Array of simulated price paths
        """
        n_steps = int(T / dt)

        # Initialize arrays
        prices = np.zeros((n_simulations, n_steps + 1))
        prices[:, 0] = S0

        rng = np.random.default_rng(random_seed)
        for t in range(1, n_steps + 1):
            # Brownian motion component
            random_shocks = rng.normal(0, 1, n_simulations)
            brownian = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * random_shocks

            # Jump component
            jump_occurs = rng.poisson(jump_intensity * dt, n_simulations)
            jump_sizes = rng.normal(jump_mean, jump_std, n_simulations) * jump_occurs

            # Update prices
            prices[:, t] = prices[:, t - 1] * np.exp(brownian + jump_sizes)

        return prices

    def mean_reverting_simulation(
        self,
        S0: float,
        theta: float,
        mu: float,
        sigma: float,
        T: float,
        dt: float,
        n_simulations: int = 1000,
        random_seed: Optional[int] = None,
    ) -> np.ndarray:
        """
        Simulate mean-reverting process (Ornstein-Uhlenbeck)

        Args:
            S0: Initial value
            theta: Mean reversion speed
            mu: Long-term mean
            sigma: Volatility
            T: Time horizon
            dt: Time step
            n_simulations: Number of simulations

        Returns:
            Array of simulated paths
        """
        n_steps = int(T / dt)

        # Initialize arrays
        values = np.zeros((n_simulations, n_steps + 1))
        values[:, 0] = S0

        # Generate random shocks
        rng = np.random.default_rng(random_seed)
        random_shocks = rng.normal(0, 1, (n_simulations, n_steps))

        for t in range(1, n_steps + 1):
            values[:, t] = (
                values[:, t - 1]
                + theta * (mu - values[:, t - 1]) * dt
                + sigma * np.sqrt(dt) * random_shocks[:, t - 1]
            )

        return values

    def var_estimation(
        self, returns: np.ndarray, confidence_levels: List[float] = [0.95, 0.99]
    ) -> Dict[float, float]:
        """
        Estimate VaR using Monte Carlo simulation results

        Args:
            returns: Array of simulated returns
            confidence_levels: List of confidence levels

        Returns:
            Dictionary with VaR estimates
        """
        var_results = {}

        for confidence in confidence_levels:
            percentile = (1 - confidence) * 100
            var_value = np.percentile(returns, percentile)
            var_results[confidence] = var_value

        return var_results

    def option_pricing_mc(
        self,
        S0: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = "call",
        n_simulations: int = 100000,
        random_seed: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Price options using Monte Carlo simulation

        Args:
            S0: Initial stock price
            K: Strike price
            T: Time to expiration
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            n_simulations: Number of simulations

        Returns:
            Dictionary with pricing results
        """
        # Simulate final stock prices
        rng = np.random.default_rng(random_seed)
        random_shocks = rng.normal(0, 1, n_simulations)
        ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * random_shocks)

        # Calculate payoffs
        if option_type == "call":
            payoffs = np.maximum(ST - K, 0)
        else:
            payoffs = np.maximum(K - ST, 0)

        # Discount to present value
        option_price = np.exp(-r * T) * np.mean(payoffs)
        price_std = np.exp(-r * T) * np.std(payoffs) / np.sqrt(n_simulations)

        # Calculate confidence interval
        confidence_interval = [
            option_price - 1.96 * price_std,
            option_price + 1.96 * price_std,
        ]

        return {
            "price": option_price,
            "std_error": price_std,
            "confidence_interval_95": confidence_interval,
            "payoffs": payoffs,
            "final_prices": ST,
        }

    def portfolio_simulation(
        self,
        initial_value: float,
        weights: np.ndarray,
        returns_data: pd.DataFrame,
        n_simulations: int = 1000,
        time_horizon: int = 252,
        random_seed: Optional[int] = None,
    ) -> Dict:
        """
        Simulate portfolio performance

        Args:
            initial_value: Initial portfolio value
            weights: Portfolio weights
            returns_data: Historical returns data
            n_simulations: Number of simulations
            time_horizon: Number of days to simulate

        Returns:
            Dictionary with simulation results
        """
        # Calculate portfolio statistics
        portfolio_returns = (returns_data * weights).sum(axis=1)
        mean_return = portfolio_returns.mean()
        volatility = portfolio_returns.std()

        # Simulate portfolio values
        portfolio_values = np.zeros((n_simulations, time_horizon + 1))
        portfolio_values[:, 0] = initial_value

        # Generate random returns
        rng = np.random.default_rng(random_seed)
        random_returns = rng.normal(
            mean_return, volatility, (n_simulations, time_horizon)
        )

        # Simulate portfolio evolution
        for t in range(1, time_horizon + 1):
            portfolio_values[:, t] = portfolio_values[:, t - 1] * (
                1 + random_returns[:, t - 1]
            )

        # Calculate final values and returns
        final_values = portfolio_values[:, -1]
        total_returns = (final_values - initial_value) / initial_value

        return {
            "portfolio_values": portfolio_values,
            "final_values": final_values,
            "total_returns": total_returns,
            "mean_final_value": np.mean(final_values),
            "std_final_value": np.std(final_values),
            "probability_loss": np.mean(total_returns < 0),
            "var_95": np.percentile(total_returns, 5),
            "var_99": np.percentile(total_returns, 1),
        }

    def plot_price_simulation(
        self,
        price_paths: np.ndarray,
        S0: float,
        T: float,
        title: str = "Stock Price Simulation",
    ) -> go.Figure:
        """
        Plot simulated price paths

        Args:
            price_paths: Array of simulated price paths
            S0: Initial price
            T: Time horizon
            title: Plot title

        Returns:
            Plotly figure
        """
        n_simulations, n_steps = price_paths.shape
        time_axis = np.linspace(0, T, n_steps)

        fig = go.Figure()

        # Plot sample paths (limit to 100 for performance)
        n_paths_to_plot = min(100, n_simulations)
        sample_indices = np.random.choice(n_simulations, n_paths_to_plot, replace=False)

        for i in sample_indices:
            fig.add_trace(
                go.Scatter(
                    x=time_axis,
                    y=price_paths[i],
                    mode="lines",
                    line=dict(width=1, color="lightblue"),
                    showlegend=False,
                    hovertemplate="Time: %{x:.2f}<br>Price: $%{y:.2f}<extra></extra>",
                )
            )

        # Add mean path
        mean_path = np.mean(price_paths, axis=0)
        fig.add_trace(
            go.Scatter(
                x=time_axis,
                y=mean_path,
                mode="lines",
                line=dict(width=3, color="red"),
                name="Mean Path",
            )
        )

        # Add confidence bands
        upper_95 = np.percentile(price_paths, 97.5, axis=0)
        lower_95 = np.percentile(price_paths, 2.5, axis=0)

        fig.add_trace(
            go.Scatter(
                x=time_axis,
                y=upper_95,
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=time_axis,
                y=lower_95,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(255, 0, 0, 0.1)",
                name="95% Confidence Band",
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Price ($)",
            hovermode="x unified",
        )

        return fig

    def plot_return_distribution(
        self, returns: np.ndarray, title: str = "Return Distribution"
    ) -> go.Figure:
        """
        Plot distribution of simulated returns

        Args:
            returns: Array of returns
            title: Plot title

        Returns:
            Plotly figure
        """
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=["Histogram", "Q-Q Plot"],
            horizontal_spacing=0.1,
        )

        # Histogram
        fig.add_trace(
            go.Histogram(
                x=returns,
                nbinsx=50,
                name="Simulated Returns",
                histnorm="probability density",
            ),
            row=1,
            col=1,
        )

        # Add normal distribution overlay
        mu, sigma = np.mean(returns), np.std(returns)
        x_range = np.linspace(returns.min(), returns.max(), 100)
        normal_pdf = stats.norm.pdf(x_range, mu, sigma)

        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=normal_pdf,
                mode="lines",
                name="Normal Distribution",
                line=dict(color="red", width=2),
            ),
            row=1,
            col=1,
        )

        # Q-Q Plot
        theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(returns)))
        sample_quantiles = np.sort(returns)

        fig.add_trace(
            go.Scatter(
                x=theoretical_quantiles,
                y=sample_quantiles,
                mode="markers",
                name="Q-Q Plot",
                marker=dict(size=4),
            ),
            row=1,
            col=2,
        )

        # Add diagonal line for Q-Q plot
        min_val = min(theoretical_quantiles.min(), sample_quantiles.min())
        max_val = max(theoretical_quantiles.max(), sample_quantiles.max())

        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode="lines",
                name="Perfect Normal",
                line=dict(color="red", dash="dash"),
            ),
            row=1,
            col=2,
        )

        fig.update_layout(title=title, showlegend=True, height=400)

        fig.update_xaxes(title_text="Returns", row=1, col=1)
        fig.update_xaxes(title_text="Theoretical Quantiles", row=1, col=2)
        fig.update_yaxes(title_text="Density", row=1, col=1)
        fig.update_yaxes(title_text="Sample Quantiles", row=1, col=2)

        return fig

    def convergence_analysis(
        self, option_prices: List[float], simulation_sizes: List[int]
    ) -> go.Figure:
        """
        Analyze Monte Carlo convergence

        Args:
            option_prices: List of option prices for different simulation sizes
            simulation_sizes: List of simulation sizes

        Returns:
            Plotly figure showing convergence
        """
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=simulation_sizes,
                y=option_prices,
                mode="lines+markers",
                name="Option Price",
                line=dict(width=3),
                marker=dict(size=8),
            )
        )

        # Add theoretical price line if available
        if len(option_prices) > 0:
            final_price = option_prices[-1]
            fig.add_hline(
                y=final_price,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Converged Price: ${final_price:.4f}",
            )

        fig.update_layout(
            title="Monte Carlo Convergence Analysis",
            xaxis_title="Number of Simulations",
            yaxis_title="Option Price ($)",
            xaxis_type="log",
        )

        return fig
