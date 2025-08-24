import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_fetcher import DataFetcher
from utils.options_pricing import BlackScholesModel
from utils.report_generator import ReportGenerator

# Configure page
st.set_page_config(
    page_title="Options Pricing",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Options Pricing & Greeks Analysis")
st.markdown("---")

# Initialize classes
data_fetcher = DataFetcher()
bs_model = BlackScholesModel()
report_generator = ReportGenerator()

# Sidebar for parameters
st.sidebar.title("⚙️ Option Parameters")

# Option specifications
st.sidebar.subheader("Option Specifications")

# Underlying asset
underlying_symbol = st.sidebar.text_input(
    "Underlying Asset Symbol",
    value="AAPL",
    help="Enter the stock symbol for the underlying asset"
).upper()

# Fetch current price
current_price = None
if underlying_symbol:
    try:
        with st.spinner(f"Fetching current price for {underlying_symbol}..."):
            stock_data = data_fetcher.fetch_stock_data(underlying_symbol, period="2d")
            if not stock_data.empty:
                current_price = stock_data['Close'].iloc[-1]
                st.sidebar.success(f"Current Price: ${current_price:.2f}")
    except Exception:
        st.sidebar.warning("Unable to fetch current price")

# Manual price input with default from fetched data
spot_price = st.sidebar.number_input(
    "Spot Price ($)",
    min_value=0.01,
    max_value=10000.0,
    value=float(current_price) if current_price else 150.0,
    step=0.01,
    format="%.2f"
)

strike_price = st.sidebar.number_input(
    "Strike Price ($)",
    min_value=0.01,
    max_value=10000.0,
    value=155.0,
    step=0.01,
    format="%.2f"
)

# Time to expiration
expiration_input = st.sidebar.selectbox(
    "Time to Expiration",
    ["Custom Days", "1 Week", "2 Weeks", "1 Month", "2 Months", "3 Months", "6 Months", "1 Year"],
    index=4
)

if expiration_input == "Custom Days":
    days_to_expiry = st.sidebar.number_input(
        "Days to Expiration",
        min_value=0.1,
        max_value=3650.0,
        value=60.0,
        step=1.0,
        format="%.1f"
    )
else:
    days_map = {
        "1 Week": 7,
        "2 Weeks": 14,
        "1 Month": 30,
        "2 Months": 60,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365
    }
    days_to_expiry = days_map[expiration_input]

time_to_expiry = days_to_expiry / 365.0

# Market parameters
st.sidebar.subheader("Market Parameters")

# Risk-free rate
risk_free_rate = st.sidebar.number_input(
    "Risk-Free Rate (%)",
    min_value=0.0,
    max_value=20.0,
    value=5.0,
    step=0.1,
    format="%.2f"
) / 100

# Volatility
volatility_input = st.sidebar.selectbox(
    "Volatility Source",
    ["Manual Input", "Historical Volatility"],
    index=0
)

if volatility_input == "Historical Volatility" and underlying_symbol:
    try:
        hist_data = data_fetcher.fetch_stock_data(underlying_symbol, period="1y")
        if not hist_data.empty:
            returns = hist_data['Close'].pct_change().dropna()
            historical_vol = returns.std() * np.sqrt(252)
            volatility = historical_vol
            st.sidebar.info(f"Historical Volatility: {historical_vol*100:.2f}%")
        else:
            volatility = 0.25
            st.sidebar.warning("Using default volatility: 25%")
    except Exception:
        volatility = 0.25
        st.sidebar.warning("Using default volatility: 25%")
else:
    volatility = st.sidebar.number_input(
        "Volatility (%)",
        min_value=0.1,
        max_value=200.0,
        value=25.0,
        step=0.1,
        format="%.2f"
    ) / 100

# Option type
option_type = st.sidebar.selectbox(
    "Option Type",
    ["call", "put"],
    index=0
)

# Analysis options
st.sidebar.subheader("Analysis Options")

show_greeks = st.sidebar.checkbox("Show Greeks Analysis", value=True)
show_sensitivity = st.sidebar.checkbox("Show Sensitivity Analysis", value=True)
show_time_decay = st.sidebar.checkbox("Show Time Decay Analysis", value=True)
show_payoff = st.sidebar.checkbox("Show Payoff Diagram", value=True)

# Calculate button
calculate_option = st.sidebar.button("🎯 Calculate Option Price", type="primary")

if calculate_option:
    try:
        # Calculate Black-Scholes price
        bs_price = bs_model.black_scholes_price(
            spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type
        )
        
        # Calculate Greeks
        greeks = bs_model.calculate_greeks(
            spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type
        )
        
        # Calculate intrinsic and time value
        if option_type == "call":
            intrinsic_value = max(spot_price - strike_price, 0)
        else:
            intrinsic_value = max(strike_price - spot_price, 0)
        
        time_value = bs_price - intrinsic_value
        
        # Determine moneyness
        moneyness_ratio = spot_price / strike_price
        if option_type == "call":
            if moneyness_ratio > 1.05:
                moneyness = "In-the-Money"
            elif moneyness_ratio < 0.95:
                moneyness = "Out-of-the-Money"
            else:
                moneyness = "At-the-Money"
        else:
            if moneyness_ratio < 0.95:
                moneyness = "In-the-Money"
            elif moneyness_ratio > 1.05:
                moneyness = "Out-of-the-Money"
            else:
                moneyness = "At-the-Money"
        
        st.success("✅ Option pricing calculation completed!")
        
        # Display key results
        st.subheader("🎯 Option Valuation Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Black-Scholes Price",
                f"${bs_price:.4f}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Intrinsic Value",
                f"${intrinsic_value:.4f}",
                delta=None
            )
        
        with col3:
            st.metric(
                "Time Value",
                f"${time_value:.4f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Moneyness",
                moneyness,
                delta=None
            )
        
        st.markdown("---")
        
        # Option specifications table
        st.subheader("📋 Option Specifications")
        
        specs_data = {
            "Parameter": [
                "Underlying Asset",
                "Spot Price",
                "Strike Price",
                "Time to Expiration",
                "Risk-Free Rate",
                "Volatility",
                "Option Type"
            ],
            "Value": [
                underlying_symbol if underlying_symbol else "N/A",
                f"${spot_price:.2f}",
                f"${strike_price:.2f}",
                f"{days_to_expiry:.1f} days ({time_to_expiry:.4f} years)",
                f"{risk_free_rate*100:.2f}%",
                f"{volatility*100:.2f}%",
                option_type.capitalize()
            ]
        }
        
        specs_df = pd.DataFrame(specs_data)
        st.dataframe(specs_df, use_container_width=True)
        
        # Greeks analysis
        if show_greeks:
            st.subheader("🔢 Greeks Analysis")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Delta", f"{greeks['delta']:.4f}")
                st.caption("Price sensitivity")
            
            with col2:
                st.metric("Gamma", f"{greeks['gamma']:.4f}")
                st.caption("Delta sensitivity")
            
            with col3:
                st.metric("Theta", f"{greeks['theta']:.4f}")
                st.caption("Time decay ($/day)")
            
            with col4:
                st.metric("Vega", f"{greeks['vega']:.4f}")
                st.caption("Volatility sensitivity")
            
            with col5:
                st.metric("Rho", f"{greeks['rho']:.4f}")
                st.caption("Interest rate sensitivity")
            
            # Greeks interpretation
            st.markdown("#### Greeks Interpretation")
            
            delta_interpretation = f"""
            **Delta ({greeks['delta']:.4f})**: For every $1 increase in the underlying price, 
            the option price will change by approximately ${greeks['delta']:.4f}.
            """
            
            gamma_interpretation = f"""
            **Gamma ({greeks['gamma']:.4f})**: Delta will change by {greeks['gamma']:.4f} 
            for every $1 move in the underlying price.
            """
            
            theta_interpretation = f"""
            **Theta ({greeks['theta']:.4f})**: The option loses approximately ${abs(greeks['theta']):.4f} 
            in value each day due to time decay.
            """
            
            vega_interpretation = f"""
            **Vega ({greeks['vega']:.4f})**: For every 1% increase in volatility, 
            the option price will increase by approximately ${greeks['vega']:.4f}.
            """
            
            st.markdown(delta_interpretation)
            st.markdown(gamma_interpretation)
            st.markdown(theta_interpretation)
            st.markdown(vega_interpretation)
        
        # Sensitivity analysis
        if show_sensitivity:
            st.subheader("📊 Sensitivity Analysis")
            
            sensitivity_fig = bs_model.plot_greeks_sensitivity(
                spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type
            )
            st.plotly_chart(sensitivity_fig, use_container_width=True)
        
        # Time decay analysis
        if show_time_decay:
            st.subheader("⏰ Time Decay Analysis")
            
            time_decay_fig = bs_model.time_decay_analysis(
                spot_price, strike_price, time_to_expiry, risk_free_rate, volatility, option_type
            )
            st.plotly_chart(time_decay_fig, use_container_width=True)
        
        # Payoff diagram
        if show_payoff:
            st.subheader("💹 Payoff Diagram")
            
            payoff_fig = bs_model.plot_option_payoff(spot_price, strike_price, option_type)
            st.plotly_chart(payoff_fig, use_container_width=True)
        
        # Volatility analysis
        st.subheader("📈 Volatility Impact Analysis")
        
        # Calculate option prices for different volatilities
        vol_range = np.linspace(0.1, 1.0, 50)
        vol_prices = []
        
        for vol in vol_range:
            price = bs_model.black_scholes_price(
                spot_price, strike_price, time_to_expiry, risk_free_rate, vol, option_type
            )
            vol_prices.append(price)
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=vol_range * 100,
            y=vol_prices,
            mode='lines',
            name='Option Price',
            line=dict(color='blue', width=3)
        ))
        
        # Current volatility marker
        fig_vol.add_vline(
            x=volatility * 100,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Current Vol: {volatility*100:.1f}%"
        )
        
        fig_vol.update_layout(
            title='Option Price vs Volatility',
            xaxis_title='Volatility (%)',
            yaxis_title='Option Price ($)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Interest rate sensitivity
        st.subheader("💰 Interest Rate Sensitivity")
        
        # Calculate option prices for different interest rates
        rate_range = np.linspace(0.001, 0.15, 50)
        rate_prices = []
        
        for rate in rate_range:
            price = bs_model.black_scholes_price(
                spot_price, strike_price, time_to_expiry, rate, volatility, option_type
            )
            rate_prices.append(price)
        
        fig_rate = go.Figure()
        fig_rate.add_trace(go.Scatter(
            x=rate_range * 100,
            y=rate_prices,
            mode='lines',
            name='Option Price',
            line=dict(color='green', width=3)
        ))
        
        # Current rate marker
        fig_rate.add_vline(
            x=risk_free_rate * 100,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Current Rate: {risk_free_rate*100:.1f}%"
        )
        
        fig_rate.update_layout(
            title='Option Price vs Interest Rate',
            xaxis_title='Risk-Free Rate (%)',
            yaxis_title='Option Price ($)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_rate, use_container_width=True)
        
        # Scenario analysis
        st.subheader("🎭 Scenario Analysis")
        
        scenarios = {
            "Current": {"spot": spot_price, "vol": volatility, "time": time_to_expiry},
            "Bull Market": {"spot": spot_price * 1.1, "vol": volatility * 0.8, "time": time_to_expiry},
            "Bear Market": {"spot": spot_price * 0.9, "vol": volatility * 1.2, "time": time_to_expiry},
            "High Volatility": {"spot": spot_price, "vol": volatility * 1.5, "time": time_to_expiry},
            "Low Volatility": {"spot": spot_price, "vol": volatility * 0.5, "time": time_to_expiry},
            "Half Time Remaining": {"spot": spot_price, "vol": volatility, "time": time_to_expiry / 2}
        }
        
        scenario_results = []
        for scenario_name, params in scenarios.items():
            scenario_price = bs_model.black_scholes_price(
                params["spot"], strike_price, params["time"], risk_free_rate, params["vol"], option_type
            )
            scenario_greeks = bs_model.calculate_greeks(
                params["spot"], strike_price, params["time"], risk_free_rate, params["vol"], option_type
            )
            
            scenario_results.append({
                "Scenario": scenario_name,
                "Spot Price": f"${params['spot']:.2f}",
                "Volatility": f"{params['vol']*100:.1f}%",
                "Time (Years)": f"{params['time']:.3f}",
                "Option Price": f"${scenario_price:.4f}",
                "Delta": f"{scenario_greeks['delta']:.4f}",
                "Theta": f"{scenario_greeks['theta']:.4f}"
            })
        
        scenario_df = pd.DataFrame(scenario_results)
        st.dataframe(scenario_df, use_container_width=True)
        
        # Export functionality
        st.subheader("📄 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Generate PDF Report"):
                with st.spinner("Generating PDF report..."):
                    option_data = {
                        'parameters': {
                            'spot_price': spot_price,
                            'strike_price': strike_price,
                            'time_to_expiry': time_to_expiry,
                            'risk_free_rate': risk_free_rate,
                            'volatility': volatility
                        },
                        'black_scholes_price': bs_price,
                        'intrinsic_value': intrinsic_value,
                        'time_value': time_value,
                        'moneyness': moneyness,
                        'greeks': greeks
                    }
                    
                    pdf_bytes = report_generator.generate_options_pricing_report(
                        option_data, option_type
                    )
                    
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"options_pricing_report_{option_type}_{underlying_symbol}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
        
        with col2:
            if st.button("📊 Export Data to CSV"):
                csv_data = {
                    'option_parameters': pd.DataFrame([{
                        'Underlying': underlying_symbol,
                        'Spot_Price': spot_price,
                        'Strike_Price': strike_price,
                        'Time_to_Expiry': time_to_expiry,
                        'Risk_Free_Rate': risk_free_rate,
                        'Volatility': volatility,
                        'Option_Type': option_type
                    }]),
                    'pricing_results': pd.DataFrame([{
                        'Black_Scholes_Price': bs_price,
                        'Intrinsic_Value': intrinsic_value,
                        'Time_Value': time_value,
                        'Moneyness': moneyness
                    }]),
                    'greeks': pd.DataFrame([greeks]),
                    'scenarios': scenario_df,
                    'volatility_sensitivity': pd.DataFrame({
                        'Volatility': vol_range,
                        'Option_Price': vol_prices
                    }),
                    'rate_sensitivity': pd.DataFrame({
                        'Interest_Rate': rate_range,
                        'Option_Price': rate_prices
                    })
                }
                
                csv_files = report_generator.export_data_to_csv(csv_data, "options_pricing")
                
                for filename, csv_bytes in csv_files.items():
                    st.download_button(
                        label=f"⬇️ Download {filename}",
                        data=csv_bytes,
                        file_name=filename,
                        mime="text/csv"
                    )
    
    except Exception as e:
        st.error(f"An error occurred during calculation: {str(e)}")
        st.exception(e)

else:
    # Initial instructions
    st.info("""
    ## 🚀 Getting Started with Options Pricing
    
    1. **Select Underlying Asset**: Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
    2. **Set Option Parameters**: Configure strike price, expiration, and option type
    3. **Choose Market Parameters**: Set risk-free rate and volatility
    4. **Select Analysis Options**: Choose which analyses to display
    5. **Calculate**: Click "Calculate Option Price" to run Black-Scholes pricing
    
    ### 🎯 Black-Scholes Model Features
    - **Fair Value Pricing**: Industry-standard option valuation
    - **Complete Greeks Calculation**: Delta, Gamma, Theta, Vega, and Rho
    - **Sensitivity Analysis**: Price sensitivity to underlying parameters
    - **Time Decay Visualization**: Theta analysis over time
    - **Volatility Impact**: Price sensitivity to implied volatility changes
    - **Scenario Analysis**: Multiple market condition evaluations
    
    ### 📊 Greeks Explained
    - **Delta (Δ)**: Price sensitivity to underlying asset price changes
    - **Gamma (Γ)**: Rate of change of delta (convexity measure)
    - **Theta (Θ)**: Time decay - option value loss per day
    - **Vega (ν)**: Sensitivity to volatility changes
    - **Rho (ρ)**: Sensitivity to interest rate changes
    
    ### 🎭 Use Cases
    - **Options Trading**: Determine fair value for trading decisions
    - **Risk Management**: Understand option sensitivities for hedging
    - **Portfolio Analysis**: Evaluate options impact on portfolio Greeks
    - **Strategy Development**: Analyze option strategies before implementation
    - **Education**: Learn options pricing theory and sensitivities
    
    ### ⚠️ Model Assumptions
    The Black-Scholes model assumes:
    - Constant volatility and risk-free rate
    - No dividends during option life
    - European-style exercise (exercise only at expiration)
    - Efficient markets with no transaction costs
    - Log-normal distribution of underlying price
    """)
    
    # Display sample calculation
    if st.button("🧮 View Sample Calculation"):
        st.markdown("### Sample Black-Scholes Calculation")
        
        # Sample parameters
        sample_spot = 100
        sample_strike = 105
        sample_time = 0.25  # 3 months
        sample_rate = 0.05
        sample_vol = 0.20
        
        # Calculate sample
        sample_price = bs_model.black_scholes_price(
            sample_spot, sample_strike, sample_time, sample_rate, sample_vol, "call"
        )
        sample_greeks = bs_model.calculate_greeks(
            sample_spot, sample_strike, sample_time, sample_rate, sample_vol, "call"
        )
        
        st.markdown(f"""
        **Sample Parameters:**
        - Spot Price: ${sample_spot}
        - Strike Price: ${sample_strike}
        - Time to Expiration: {sample_time} years (3 months)
        - Risk-free Rate: {sample_rate*100}%
        - Volatility: {sample_vol*100}%
        - Option Type: Call
        
        **Results:**
        - **Option Price**: ${sample_price:.4f}
        - **Delta**: {sample_greeks['delta']:.4f}
        - **Gamma**: {sample_greeks['gamma']:.4f}
        - **Theta**: {sample_greeks['theta']:.4f}
        - **Vega**: {sample_greeks['vega']:.4f}
        - **Rho**: {sample_greeks['rho']:.4f}
        """)
        
        st.caption("This is a sample calculation. Use the sidebar to input your own parameters.")
