import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantrisk.data.fetcher import DataFetcher
from quantrisk.analytics.monte_carlo import MonteCarloSimulation
from quantrisk.analytics.options import BlackScholesModel
from quantrisk.analytics.risk import RiskAnalytics
from quantrisk.utils.reports import ReportGenerator

# Configure page
st.set_page_config(
    page_title="Monte Carlo Simulation",
    page_icon="🎲",
    layout="wide"
)

st.title("🎲 Monte Carlo Simulation")
st.markdown("---")

# Initialize classes
data_fetcher = DataFetcher()
mc_simulator = MonteCarloSimulation()
bs_model = BlackScholesModel()
risk_analyzer = RiskAnalytics()
report_generator = ReportGenerator()

# Sidebar for parameters
st.sidebar.title("🎲 Simulation Parameters")

# Simulation type
simulation_type = st.sidebar.selectbox(
    "Simulation Type",
    [
        "Stock Price Simulation", 
        "Portfolio Simulation", 
        "Options Pricing", 
        "VaR Estimation",
        "Jump Diffusion Model",
        "Mean Reversion Model"
    ],
    index=0
)

st.sidebar.markdown("---")

# Common parameters
st.sidebar.subheader("General Parameters")

n_simulations = st.sidebar.selectbox(
    "Number of Simulations",
    [1000, 5000, 10000, 25000, 50000, 100000],
    index=2,
    help="More simulations provide more accurate results but take longer"
)

time_horizon = st.sidebar.selectbox(
    "Time Horizon",
    ["1 Week", "2 Weeks", "1 Month", "2 Months", "3 Months", "6 Months", "1 Year", "2 Years"],
    index=6
)

# Convert time horizon to years
time_map = {
    "1 Week": 7/365,
    "2 Weeks": 14/365,
    "1 Month": 30/365,
    "2 Months": 60/365,
    "3 Months": 90/365,
    "6 Months": 180/365,
    "1 Year": 1.0,
    "2 Years": 2.0
}
T = time_map[time_horizon]

time_steps = st.sidebar.slider(
    "Time Steps",
    min_value=10,
    max_value=1000,
    value=int(T * 252),  # Daily steps
    step=10,
    help="Number of time steps in simulation"
)

dt = T / time_steps

if simulation_type == "Stock Price Simulation":
    st.sidebar.subheader("Stock Parameters")
    
    symbol = st.sidebar.text_input(
        "Stock Symbol",
        value="AAPL",
        help="Enter stock symbol for analysis"
    ).upper()
    
    # Fetch current data
    current_price = None
    historical_vol = None
    historical_return = None
    
    if symbol:
        try:
            with st.spinner(f"Fetching data for {symbol}..."):
                stock_data = data_fetcher.fetch_stock_data(symbol, period="1y")
                if not stock_data.empty:
                    current_price = stock_data['Close'].iloc[-1]
                    returns = stock_data['Close'].pct_change().dropna()
                    historical_vol = returns.std() * np.sqrt(252)
                    historical_return = returns.mean() * 252
                    st.sidebar.success(f"Current Price: ${current_price:.2f}")
                    st.sidebar.info(f"Historical Vol: {historical_vol*100:.1f}%")
        except Exception:
            st.sidebar.warning("Unable to fetch stock data")
    
    initial_price = st.sidebar.number_input(
        "Initial Stock Price ($)",
        min_value=0.01,
        max_value=10000.0,
        value=float(current_price) if current_price else 100.0,
        step=0.01,
        format="%.2f"
    )
    
    # Use historical data or manual input
    use_historical = st.sidebar.checkbox(
        "Use Historical Parameters",
        value=True if historical_vol else False,
        disabled=not historical_vol
    )
    
    if use_historical and historical_vol:
        mu = historical_return
        sigma = historical_vol
        st.sidebar.info(f"Using historical μ={mu*100:.1f}%, σ={sigma*100:.1f}%")
    else:
        mu = st.sidebar.number_input(
            "Expected Return (% annual)",
            min_value=-50.0,
            max_value=100.0,
            value=10.0,
            step=1.0,
            format="%.1f"
        ) / 100
        
        sigma = st.sidebar.number_input(
            "Volatility (% annual)",
            min_value=1.0,
            max_value=200.0,
            value=25.0,
            step=1.0,
            format="%.1f"
        ) / 100

elif simulation_type == "Portfolio Simulation":
    st.sidebar.subheader("Portfolio Parameters")
    
    symbols_input = st.sidebar.text_area(
        "Portfolio Symbols (one per line)",
        value="AAPL\nGOOGL\nMSFT\nTSLA\nAMZN",
        height=120
    )
    
    symbols = [s.strip().upper() for s in symbols_input.strip().split('\n') if s.strip()]
    
    initial_value = st.sidebar.number_input(
        "Initial Portfolio Value ($)",
        min_value=1000.0,
        max_value=10000000.0,
        value=100000.0,
        step=1000.0,
        format="%.0f"
    )
    
    equal_weights = st.sidebar.checkbox("Equal Weights", value=True)

elif simulation_type == "Options Pricing":
    st.sidebar.subheader("Option Parameters")
    
    underlying_symbol = st.sidebar.text_input(
        "Underlying Symbol",
        value="AAPL"
    ).upper()
    
    # Fetch current price
    current_price = None
    if underlying_symbol:
        try:
            stock_data = data_fetcher.fetch_stock_data(underlying_symbol, period="2d")
            if not stock_data.empty:
                current_price = stock_data['Close'].iloc[-1]
                st.sidebar.success(f"Current Price: ${current_price:.2f}")
        except Exception:
            pass
    
    S0 = st.sidebar.number_input(
        "Current Stock Price ($)",
        min_value=0.01,
        value=float(current_price) if current_price else 100.0,
        step=0.01,
        format="%.2f"
    )
    
    K = st.sidebar.number_input(
        "Strike Price ($)",
        min_value=0.01,
        value=105.0,
        step=0.01,
        format="%.2f"
    )
    
    r = st.sidebar.number_input(
        "Risk-Free Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.1
    ) / 100
    
    sigma = st.sidebar.number_input(
        "Volatility (%)",
        min_value=1.0,
        max_value=200.0,
        value=25.0,
        step=1.0
    ) / 100
    
    option_type = st.sidebar.selectbox("Option Type", ["call", "put"])

elif simulation_type == "Jump Diffusion Model":
    st.sidebar.subheader("Jump Diffusion Parameters")
    
    S0 = st.sidebar.number_input(
        "Initial Price ($)",
        min_value=0.01,
        value=100.0,
        step=0.01
    )
    
    mu = st.sidebar.number_input(
        "Drift (%)",
        min_value=-50.0,
        max_value=50.0,
        value=10.0,
        step=1.0
    ) / 100
    
    sigma = st.sidebar.number_input(
        "Diffusion Volatility (%)",
        min_value=1.0,
        max_value=100.0,
        value=20.0,
        step=1.0
    ) / 100
    
    jump_intensity = st.sidebar.number_input(
        "Jump Intensity (per year)",
        min_value=0.0,
        max_value=50.0,
        value=5.0,
        step=0.5
    )
    
    jump_mean = st.sidebar.number_input(
        "Jump Mean (%)",
        min_value=-50.0,
        max_value=50.0,
        value=-5.0,
        step=1.0
    ) / 100
    
    jump_std = st.sidebar.number_input(
        "Jump Std Dev (%)",
        min_value=1.0,
        max_value=100.0,
        value=15.0,
        step=1.0
    ) / 100

elif simulation_type == "Mean Reversion Model":
    st.sidebar.subheader("Mean Reversion Parameters")
    
    S0 = st.sidebar.number_input(
        "Initial Value",
        min_value=0.01,
        value=100.0,
        step=0.01
    )
    
    theta = st.sidebar.number_input(
        "Mean Reversion Speed",
        min_value=0.1,
        max_value=10.0,
        value=2.0,
        step=0.1
    )
    
    mu_lr = st.sidebar.number_input(
        "Long-term Mean",
        min_value=0.01,
        value=100.0,
        step=0.01
    )
    
    sigma_mr = st.sidebar.number_input(
        "Volatility",
        min_value=0.01,
        value=20.0,
        step=0.01
    )

# VaR parameters
if simulation_type == "VaR Estimation":
    st.sidebar.subheader("VaR Parameters")
    
    portfolio_value = st.sidebar.number_input(
        "Portfolio Value ($)",
        min_value=1000.0,
        value=1000000.0,
        step=1000.0,
        format="%.0f"
    )
    
    confidence_levels = st.sidebar.multiselect(
        "Confidence Levels",
        [0.90, 0.95, 0.99],
        default=[0.95, 0.99]
    )

# Run simulation button
run_simulation = st.sidebar.button("🎲 Run Simulation", type="primary")

if run_simulation:
    try:
        with st.spinner("Running Monte Carlo simulation..."):
            
            if simulation_type == "Stock Price Simulation":
                # Generate stock price paths
                price_paths = mc_simulator.geometric_brownian_motion(
                    initial_price, mu, sigma, T, dt, n_simulations
                )
                
                st.success("✅ Stock price simulation completed!")
                
                # Display results
                st.subheader("📈 Simulation Results")
                
                # Key statistics
                final_prices = price_paths[:, -1]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    mean_final = np.mean(final_prices)
                    st.metric("Mean Final Price", f"${mean_final:.2f}")
                
                with col2:
                    std_final = np.std(final_prices)
                    st.metric("Standard Deviation", f"${std_final:.2f}")
                
                with col3:
                    prob_gain = np.mean(final_prices > initial_price) * 100
                    st.metric("Probability of Gain", f"{prob_gain:.1f}%")
                
                with col4:
                    max_price = np.max(final_prices)
                    st.metric("Maximum Price", f"${max_price:.2f}")
                
                # Plot simulation paths
                st.subheader("📊 Price Path Simulation")
                
                price_fig = mc_simulator.plot_price_simulation(
                    price_paths, initial_price, T, 
                    f"{symbol} Stock Price Simulation" if symbol else "Stock Price Simulation"
                )
                st.plotly_chart(price_fig, use_container_width=True)
                
                # Return distribution
                st.subheader("📊 Return Distribution")
                
                returns = (final_prices - initial_price) / initial_price
                
                return_fig = mc_simulator.plot_return_distribution(
                    returns, f"{time_horizon} Return Distribution"
                )
                st.plotly_chart(return_fig, use_container_width=True)
                
                # Distribution statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Mean Return", f"{np.mean(returns)*100:.2f}%")
                
                with col2:
                    st.metric("Return Volatility", f"{np.std(returns)*100:.2f}%")
                
                with col3:
                    percentile_5 = np.percentile(returns, 5) * 100
                    st.metric("5th Percentile", f"{percentile_5:.2f}%")
                
                with col4:
                    percentile_95 = np.percentile(returns, 95) * 100
                    st.metric("95th Percentile", f"{percentile_95:.2f}%")
            
            elif simulation_type == "Portfolio Simulation":
                # Validate symbols and fetch data
                valid_symbols = data_fetcher.validate_symbols(symbols)
                
                if len(valid_symbols) < 2:
                    st.error("At least 2 valid symbols required for portfolio simulation")
                    st.stop()
                
                returns_data = data_fetcher.get_returns_matrix(valid_symbols, "1y")
                
                if returns_data.empty:
                    st.error("Unable to fetch sufficient data for simulation")
                    st.stop()
                
                # Set weights
                if equal_weights:
                    weights = np.array([1.0/len(valid_symbols)] * len(valid_symbols))
                else:
                    # For simplicity, use equal weights in this implementation
                    weights = np.array([1.0/len(valid_symbols)] * len(valid_symbols))
                
                # Run portfolio simulation
                portfolio_results = mc_simulator.portfolio_simulation(
                    initial_value, weights, returns_data, n_simulations, time_steps
                )
                
                st.success("✅ Portfolio simulation completed!")
                
                # Display results
                st.subheader("💼 Portfolio Simulation Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    mean_final = portfolio_results['mean_final_value']
                    st.metric("Mean Final Value", f"${mean_final:,.0f}")
                
                with col2:
                    prob_loss = portfolio_results['probability_loss'] * 100
                    st.metric("Probability of Loss", f"{prob_loss:.1f}%")
                
                with col3:
                    var_95 = abs(portfolio_results['var_95']) * 100
                    st.metric("VaR (95%)", f"{var_95:.1f}%")
                
                with col4:
                    var_99 = abs(portfolio_results['var_99']) * 100
                    st.metric("VaR (99%)", f"{var_99:.1f}%")
                
                # Plot portfolio evolution
                st.subheader("📈 Portfolio Value Evolution")
                
                portfolio_fig = mc_simulator.plot_price_simulation(
                    portfolio_results['portfolio_values'], initial_value, T,
                    f"Portfolio Value Simulation ({len(valid_symbols)} assets)"
                )
                st.plotly_chart(portfolio_fig, use_container_width=True)
                
                # Return distribution
                return_dist_fig = mc_simulator.plot_return_distribution(
                    portfolio_results['total_returns'],
                    "Portfolio Return Distribution"
                )
                st.plotly_chart(return_dist_fig, use_container_width=True)
            
            elif simulation_type == "Options Pricing":
                # Monte Carlo option pricing
                option_results = mc_simulator.option_pricing_mc(
                    S0, K, T, r, sigma, option_type, n_simulations
                )
                
                # Black-Scholes comparison
                bs_price = bs_model.black_scholes_price(S0, K, T, r, sigma, option_type)
                
                st.success("✅ Options pricing simulation completed!")
                
                # Display results
                st.subheader("🎯 Option Pricing Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    mc_price = option_results['price']
                    st.metric("Monte Carlo Price", f"${mc_price:.4f}")
                
                with col2:
                    st.metric("Black-Scholes Price", f"${bs_price:.4f}")
                
                with col3:
                    price_diff = abs(mc_price - bs_price)
                    st.metric("Price Difference", f"${price_diff:.4f}")
                
                with col4:
                    std_error = option_results['std_error']
                    st.metric("Standard Error", f"${std_error:.4f}")
                
                # Confidence interval
                ci_lower, ci_upper = option_results['confidence_interval_95']
                st.info(f"95% Confidence Interval: ${ci_lower:.4f} - ${ci_upper:.4f}")
                
                # Final price distribution
                st.subheader("📊 Final Stock Price Distribution")
                
                fig_final_prices = go.Figure()
                fig_final_prices.add_trace(go.Histogram(
                    x=option_results['final_prices'],
                    nbinsx=50,
                    name='Final Prices',
                    opacity=0.7
                ))
                
                # Add strike price line
                fig_final_prices.add_vline(
                    x=K,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Strike: ${K:.2f}"
                )
                
                fig_final_prices.update_layout(
                    title='Distribution of Final Stock Prices',
                    xaxis_title='Stock Price ($)',
                    yaxis_title='Frequency'
                )
                
                st.plotly_chart(fig_final_prices, use_container_width=True)
                
                # Payoff distribution
                st.subheader("💰 Option Payoff Distribution")
                
                fig_payoffs = go.Figure()
                fig_payoffs.add_trace(go.Histogram(
                    x=option_results['payoffs'],
                    nbinsx=50,
                    name='Payoffs',
                    opacity=0.7
                ))
                
                fig_payoffs.update_layout(
                    title='Distribution of Option Payoffs',
                    xaxis_title='Payoff ($)',
                    yaxis_title='Frequency'
                )
                
                st.plotly_chart(fig_payoffs, use_container_width=True)
                
                # Convergence analysis
                st.subheader("📈 Convergence Analysis")
                
                # Calculate prices for different simulation sizes
                sim_sizes = [100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
                sim_sizes = [s for s in sim_sizes if s <= n_simulations]
                
                convergence_prices = []
                for size in sim_sizes:
                    subset_payoffs = option_results['payoffs'][:size]
                    subset_price = np.exp(-r * T) * np.mean(subset_payoffs)
                    convergence_prices.append(subset_price)
                
                convergence_fig = mc_simulator.convergence_analysis(convergence_prices, sim_sizes)
                st.plotly_chart(convergence_fig, use_container_width=True)
            
            elif simulation_type == "Jump Diffusion Model":
                # Generate jump diffusion paths
                price_paths = mc_simulator.jump_diffusion_simulation(
                    S0, mu, sigma, jump_intensity, jump_mean, jump_std, T, dt, n_simulations
                )
                
                st.success("✅ Jump diffusion simulation completed!")
                
                # Compare with geometric Brownian motion
                gbm_paths = mc_simulator.geometric_brownian_motion(
                    S0, mu, sigma, T, dt, 1000
                )
                
                # Display results
                st.subheader("📈 Jump Diffusion vs GBM Comparison")
                
                # Statistics comparison
                jump_final = price_paths[:, -1]
                gbm_final = gbm_paths[:, -1]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Jump Diffusion Model**")
                    st.metric("Mean Final Price", f"${np.mean(jump_final):.2f}")
                    st.metric("Standard Deviation", f"${np.std(jump_final):.2f}")
                    st.metric("Skewness", f"{np.mean((jump_final - np.mean(jump_final))**3) / np.std(jump_final)**3:.3f}")
                
                with col2:
                    st.markdown("**Geometric Brownian Motion**")
                    st.metric("Mean Final Price", f"${np.mean(gbm_final):.2f}")
                    st.metric("Standard Deviation", f"${np.std(gbm_final):.2f}")
                    st.metric("Skewness", f"{np.mean((gbm_final - np.mean(gbm_final))**3) / np.std(gbm_final)**3:.3f}")
                
                # Plot comparison
                fig_comparison = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=['Sample Price Paths', 'Final Price Distributions']
                )
                
                # Sample paths
                for i in range(min(10, n_simulations)):
                    time_axis = np.linspace(0, T, price_paths.shape[1])
                    fig_comparison.add_trace(go.Scatter(
                        x=time_axis,
                        y=price_paths[i],
                        mode='lines',
                        line=dict(width=1, color='blue'),
                        showlegend=False if i > 0 else True,
                        name='Jump Diffusion' if i == 0 else None
                    ), row=1, col=1)
                
                for i in range(min(10, len(gbm_paths))):
                    fig_comparison.add_trace(go.Scatter(
                        x=time_axis,
                        y=gbm_paths[i],
                        mode='lines',
                        line=dict(width=1, color='red'),
                        showlegend=False if i > 0 else True,
                        name='GBM' if i == 0 else None
                    ), row=1, col=1)
                
                # Final price distributions
                fig_comparison.add_trace(go.Histogram(
                    x=jump_final,
                    name='Jump Diffusion',
                    opacity=0.7,
                    nbinsx=30
                ), row=2, col=1)
                
                fig_comparison.add_trace(go.Histogram(
                    x=gbm_final,
                    name='GBM',
                    opacity=0.7,
                    nbinsx=30
                ), row=2, col=1)
                
                fig_comparison.update_layout(
                    title='Jump Diffusion vs Geometric Brownian Motion',
                    height=800
                )
                
                st.plotly_chart(fig_comparison, use_container_width=True)
            
            elif simulation_type == "Mean Reversion Model":
                # Generate mean-reverting paths
                price_paths = mc_simulator.mean_reverting_simulation(
                    S0, theta, mu_lr, sigma_mr, T, dt, n_simulations
                )
                
                st.success("✅ Mean reversion simulation completed!")
                
                # Display results
                st.subheader("🔄 Mean Reversion Results")
                
                final_values = price_paths[:, -1]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Mean Final Value", f"{np.mean(final_values):.2f}")
                
                with col2:
                    st.metric("Long-term Mean", f"{mu_lr:.2f}")
                
                with col3:
                    convergence = np.mean(np.abs(final_values - mu_lr))
                    st.metric("Mean Deviation from LT Mean", f"{convergence:.2f}")
                
                with col4:
                    reversion_strength = 1 - np.exp(-theta * T)
                    st.metric("Reversion Strength", f"{reversion_strength:.3f}")
                
                # Plot paths
                mr_fig = mc_simulator.plot_price_simulation(
                    price_paths, S0, T, "Mean Reverting Process"
                )
                
                # Add long-term mean line
                mr_fig.add_hline(
                    y=mu_lr,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"Long-term Mean: {mu_lr:.2f}"
                )
                
                st.plotly_chart(mr_fig, use_container_width=True)
                
                # Show convergence over time
                st.subheader("📊 Convergence to Long-term Mean")
                
                time_axis = np.linspace(0, T, price_paths.shape[1])
                mean_path = np.mean(price_paths, axis=0)
                std_path = np.std(price_paths, axis=0)
                
                fig_convergence = go.Figure()
                
                fig_convergence.add_trace(go.Scatter(
                    x=time_axis,
                    y=mean_path,
                    mode='lines',
                    name='Mean Path',
                    line=dict(color='blue', width=3)
                ))
                
                fig_convergence.add_trace(go.Scatter(
                    x=time_axis,
                    y=mean_path + std_path,
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig_convergence.add_trace(go.Scatter(
                    x=time_axis,
                    y=mean_path - std_path,
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    name='±1 Std Dev',
                    fillcolor='rgba(0,100,80,0.2)'
                ))
                
                fig_convergence.add_hline(
                    y=mu_lr,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Long-term Mean"
                )
                
                fig_convergence.update_layout(
                    title='Mean Reversion Convergence',
                    xaxis_title='Time',
                    yaxis_title='Value'
                )
                
                st.plotly_chart(fig_convergence, use_container_width=True)
            
            # Export functionality
            st.subheader("📄 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Export Data to CSV"):
                    csv_data = {}
                    
                    if simulation_type == "Stock Price Simulation":
                        csv_data['simulation_parameters'] = pd.DataFrame([{
                            'Symbol': symbol if symbol else 'N/A',
                            'Initial_Price': initial_price,
                            'Expected_Return': mu,
                            'Volatility': sigma,
                            'Time_Horizon': T,
                            'Simulations': n_simulations
                        }])
                        csv_data['final_prices'] = pd.DataFrame({'Final_Price': price_paths[:, -1]})
                        csv_data['statistics'] = pd.DataFrame([{
                            'Mean_Final_Price': np.mean(price_paths[:, -1]),
                            'Std_Final_Price': np.std(price_paths[:, -1]),
                            'Min_Price': np.min(price_paths[:, -1]),
                            'Max_Price': np.max(price_paths[:, -1])
                        }])
                    
                    elif simulation_type == "Options Pricing":
                        csv_data['option_parameters'] = pd.DataFrame([{
                            'Underlying_Price': S0,
                            'Strike_Price': K,
                            'Time_to_Expiry': T,
                            'Risk_Free_Rate': r,
                            'Volatility': sigma,
                            'Option_Type': option_type,
                            'Simulations': n_simulations
                        }])
                        csv_data['pricing_results'] = pd.DataFrame([{
                            'Monte_Carlo_Price': option_results['price'],
                            'Black_Scholes_Price': bs_price,
                            'Standard_Error': option_results['std_error']
                        }])
                        csv_data['final_prices'] = pd.DataFrame({'Final_Stock_Price': option_results['final_prices']})
                        csv_data['payoffs'] = pd.DataFrame({'Option_Payoff': option_results['payoffs']})
                    
                    csv_files = report_generator.export_data_to_csv(csv_data, "monte_carlo_simulation")
                    
                    for filename, csv_bytes in csv_files.items():
                        st.download_button(
                            label=f"⬇️ Download {filename}",
                            data=csv_bytes,
                            file_name=filename,
                            mime="text/csv"
                        )
            
            with col2:
                st.info("PDF report generation available for specific analysis types")
    
    except Exception as e:
        st.error(f"An error occurred during simulation: {str(e)}")
        st.exception(e)

else:
    # Initial instructions
    st.info("""
    ## 🚀 Getting Started with Monte Carlo Simulation
    
    1. **Choose Simulation Type**: Select the type of financial model to simulate
    2. **Set Parameters**: Configure model parameters and simulation settings
    3. **Run Simulation**: Click "Run Simulation" to generate Monte Carlo paths
    4. **Analyze Results**: Review statistical output and visualizations
    
    ### 🎲 Available Simulation Models
    
    #### 📈 Stock Price Simulation (Geometric Brownian Motion)
    - Models stock price evolution with constant drift and volatility
    - Used for basic price forecasting and risk assessment
    - Assumes log-normal price distribution
    
    #### 💼 Portfolio Simulation
    - Simulates multi-asset portfolio performance
    - Incorporates correlation between assets
    - Provides VaR and expected shortfall estimates
    
    #### 🎯 Options Pricing
    - Monte Carlo alternative to Black-Scholes
    - Handles complex payoff structures
    - Provides confidence intervals for option values
    
    #### ⚠️ VaR Estimation
    - Risk assessment through simulation
    - Tail risk analysis
    - Regulatory capital calculations
    
    #### 🦘 Jump Diffusion Model
    - Incorporates sudden price jumps
    - Models market crashes and volatility spikes
    - More realistic than pure Brownian motion
    
    #### 🔄 Mean Reversion Model
    - Models mean-reverting processes
    - Suitable for interest rates, volatility
    - Ornstein-Uhlenbeck process implementation
    
    ### 📊 Key Benefits
    - **Flexibility**: Handle complex models not solvable analytically
    - **Accuracy**: Results improve with more simulations
    - **Risk Assessment**: Generate full distribution of outcomes
    - **Scenario Analysis**: Test multiple market conditions
    - **Confidence Intervals**: Quantify estimation uncertainty
    
    ### 🎯 Applications
    - **Risk Management**: VaR and stress testing
    - **Derivatives Pricing**: Complex option valuation
    - **Portfolio Optimization**: Expected returns and risk
    - **Regulatory Compliance**: Capital requirement calculations
    - **Research**: Financial model validation and testing
    """)
    
    # Show sample simulation
    if st.button("🎲 View Sample Simulation"):
        st.markdown("### Sample Geometric Brownian Motion")
        
        # Generate sample paths
        np.random.seed(42)  # For reproducibility
        sample_paths = mc_simulator.geometric_brownian_motion(
            S0=100, mu=0.1, sigma=0.2, T=1.0, dt=1/252, n_simulations=1000
        )
        
        # Plot sample paths
        sample_fig = mc_simulator.plot_price_simulation(
            sample_paths, 100, 1.0, "Sample Stock Price Simulation"
        )
        st.plotly_chart(sample_fig, use_container_width=True)
        
        # Sample statistics
        final_prices = sample_paths[:, -1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean Final Price", f"${np.mean(final_prices):.2f}")
        
        with col2:
            st.metric("Standard Deviation", f"${np.std(final_prices):.2f}")
        
        with col3:
            st.metric("Probability of Gain", f"{np.mean(final_prices > 100)*100:.1f}%")
        
        with col4:
            st.metric("95th Percentile", f"${np.percentile(final_prices, 95):.2f}")
        
        st.caption("This is a sample simulation with S₀=$100, μ=10%, σ=20%, T=1 year, 1000 simulations")
