import streamlit as st
import pandas as pd
import numpy as np
from quantrisk.data.fetcher import DataFetcher
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Quantitative Finance Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🏦 Quantitative Finance Analytics Platform</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Professional-grade quantitative finance analytics for institutional risk assessment, portfolio optimization, and derivatives pricing
    
    Welcome to a comprehensive financial analytics platform that implements industry-standard models used by investment banks and hedge funds.
    """)
    
    # Sidebar navigation
    st.sidebar.title("📊 Analytics Dashboard")
    st.sidebar.markdown("---")
    
    # Quick market overview
    st.subheader("📈 Market Overview")
    
    try:
        data_fetcher = DataFetcher()
        
        # Major indices
        indices = {
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "Dow Jones": "^DJI",
            "VIX": "^VIX"
        }
        
        col1, col2, col3, col4 = st.columns(4)
        
        for i, (name, symbol) in enumerate(indices.items()):
            try:
                data = data_fetcher.fetch_stock_data(symbol, period="2d")
                if len(data) >= 2:
                    current_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2]
                    change = ((current_price - prev_price) / prev_price) * 100
                    
                    col = [col1, col2, col3, col4][i]
                    with col:
                        st.metric(
                            label=name,
                            value=f"${current_price:.2f}" if symbol != "^VIX" else f"{current_price:.2f}",
                            delta=f"{change:.2f}%"
                        )
            except Exception as e:
                col = [col1, col2, col3, col4][i]
                with col:
                    st.metric(label=name, value="N/A", delta="0.00%")
    
    except Exception as e:
        st.error(f"Unable to fetch market data: {str(e)}")
    
    st.markdown("---")
    
    # Platform features
    st.subheader("🛠️ Platform Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📊 Risk Analytics
        - Value at Risk (VaR) at 95% & 99% confidence
        - Conditional VaR for tail risk assessment
        - Sharpe ratio and risk-adjusted returns
        - Maximum drawdown analysis
        - Monte Carlo simulations
        """)
        
        st.markdown("""
        #### 💼 Portfolio Optimization
        - Efficient frontier visualization
        - Mean-variance optimization
        - Sharpe ratio maximization
        - Minimum volatility portfolios
        - Correlation analysis
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 Options Pricing
        - Black-Scholes valuation
        - Complete Greeks calculation
        - Sensitivity analysis
        - Time decay visualization
        - Volatility impact analysis
        """)
        
        st.markdown("""
        #### 🔄 Pairs Trading
        - Cointegration testing
        - Hedge ratio calculation
        - Z-score monitoring
        - Signal generation
        - Statistical significance testing
        """)
    
    st.markdown("---")
    
    # Quick start guide
    st.subheader("🚀 Quick Start Guide")
    
    st.markdown("""
    1. **Risk Analytics**: Navigate to analyze portfolio risk metrics and VaR calculations
    2. **Portfolio Optimization**: Build optimal portfolios using modern portfolio theory
    3. **Options Pricing**: Price options and calculate Greeks using Black-Scholes model
    4. **Monte Carlo**: Run probabilistic simulations for price forecasting
    5. **Pairs Trading**: Identify statistical arbitrage opportunities
    
    Use the sidebar navigation to access each module. All analyses support professional PDF and CSV exports.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>Professional-grade quantitative finance analytics platform</p>
        <p>Built with institutional standards for risk assessment and portfolio optimization</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
