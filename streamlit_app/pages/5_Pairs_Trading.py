import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantrisk.data.fetcher import DataFetcher
from quantrisk.analytics.pairs_trading import PairsTrading
from quantrisk.utils.reports import ReportGenerator

# Configure page
st.set_page_config(
    page_title="Pairs Trading",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Pairs Trading & Statistical Arbitrage")
st.markdown("---")

# Initialize classes
data_fetcher = DataFetcher()
pairs_analyzer = PairsTrading()
report_generator = ReportGenerator()

# Sidebar for parameters
st.sidebar.title("🔄 Pairs Trading Parameters")

# Asset pair selection
st.sidebar.subheader("Asset Pair Selection")

# Method for selecting pairs
selection_method = st.sidebar.selectbox(
    "Pair Selection Method",
    ["Manual Selection", "Sector Screening", "Popular Pairs"],
    index=0
)

if selection_method == "Manual Selection":
    stock1 = st.sidebar.text_input(
        "Stock 1 Symbol",
        value="AAPL",
        help="Enter the first stock symbol"
    ).upper()
    
    stock2 = st.sidebar.text_input(
        "Stock 2 Symbol", 
        value="MSFT",
        help="Enter the second stock symbol"
    ).upper()

elif selection_method == "Sector Screening":
    sector_pairs = {
        "Technology": [("AAPL", "MSFT"), ("GOOGL", "META"), ("NVDA", "AMD"), ("CRM", "ORCL")],
        "Banking": [("JPM", "BAC"), ("WFC", "C"), ("GS", "MS"), ("USB", "PNC")],
        "Energy": [("XOM", "CVX"), ("COP", "EOG"), ("SLB", "HAL"), ("MPC", "VLO")],
        "Retail": [("WMT", "TGT"), ("HD", "LOW"), ("COST", "BJ"), ("AMZN", "EBAY")],
        "Healthcare": [("JNJ", "PFE"), ("UNH", "CVS"), ("ABBV", "BMY"), ("MRK", "LLY")],
        "Telecom": [("VZ", "T"), ("TMUS", "S"), ("CHTR", "CMCSA")],
        "Airlines": [("DAL", "UAL"), ("AAL", "LUV"), ("JBLU", "ALK")]
    }
    
    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        list(sector_pairs.keys())
    )
    
    pair_options = [f"{pair[0]} vs {pair[1]}" for pair in sector_pairs[selected_sector]]
    selected_pair_str = st.sidebar.selectbox(
        "Select Pair",
        pair_options
    )
    
    # Extract symbols from selection
    stock1, stock2 = selected_pair_str.split(" vs ")

elif selection_method == "Popular Pairs":
    popular_pairs = [
        ("AAPL", "MSFT", "Tech Giants"),
        ("JPM", "BAC", "Major Banks"),
        ("XOM", "CVX", "Oil Majors"),
        ("KO", "PEP", "Beverage Rivals"),
        ("WMT", "TGT", "Retail Chains"),
        ("VZ", "T", "Telecom Leaders"),
        ("JNJ", "PFE", "Pharma Giants"),
        ("HD", "LOW", "Home Improvement"),
        ("GOOGL", "META", "Internet Giants"),
        ("GS", "MS", "Investment Banks")
    ]
    
    pair_options = [f"{pair[0]} vs {pair[1]} ({pair[2]})" for pair in popular_pairs]
    selected_pair_str = st.sidebar.selectbox(
        "Select Popular Pair",
        pair_options
    )
    
    # Extract symbols from selection
    stock1 = selected_pair_str.split(" vs ")[0]
    stock2 = selected_pair_str.split(" vs ")[1].split(" (")[0]

# Time period
period = st.sidebar.selectbox(
    "Analysis Period",
    ["6mo", "1y", "2y", "3y", "5y"],
    index=1,
    help="Time period for cointegration and correlation analysis"
)

# Analysis parameters
st.sidebar.subheader("Analysis Parameters")

lookback_window = st.sidebar.slider(
    "Lookback Window (days)",
    min_value=10,
    max_value=100,
    value=20,
    step=5,
    help="Rolling window for z-score calculation"
)

entry_threshold = st.sidebar.number_input(
    "Entry Threshold (z-score)",
    min_value=1.0,
    max_value=5.0,
    value=2.0,
    step=0.1,
    help="Z-score threshold for trade entry signals"
)

exit_threshold = st.sidebar.number_input(
    "Exit Threshold (z-score)",
    min_value=0.1,
    max_value=2.0,
    value=0.5,
    step=0.1,
    help="Z-score threshold for trade exit signals"
)

# Analysis options
st.sidebar.subheader("Analysis Options")

show_cointegration = st.sidebar.checkbox("Cointegration Test", value=True)
show_spread_analysis = st.sidebar.checkbox("Spread Analysis", value=True)
show_trading_signals = st.sidebar.checkbox("Trading Signals", value=True)
show_backtest = st.sidebar.checkbox("Strategy Backtest", value=True)

# Run analysis button
run_analysis = st.sidebar.button("🔍 Analyze Pair", type="primary")

if run_analysis and stock1 and stock2:
    try:
        with st.spinner(f"Analyzing {stock1} vs {stock2} pair..."):
            # Validate symbols
            valid_symbols = data_fetcher.validate_symbols([stock1, stock2])
            
            if len(valid_symbols) != 2:
                st.error(f"Invalid symbols. Please check: {stock1}, {stock2}")
                st.stop()
            
            # Fetch data for both stocks
            stock1_data = data_fetcher.fetch_stock_data(stock1, period)
            stock2_data = data_fetcher.fetch_stock_data(stock2, period)
            
            if stock1_data.empty or stock2_data.empty:
                st.error("Unable to fetch sufficient data for analysis.")
                st.stop()
            
            # Extract closing prices
            stock1_prices = stock1_data['Close']
            stock2_prices = stock2_data['Close']
            
            # Get stock info
            stock1_info = data_fetcher.get_stock_info(stock1)
            stock2_info = data_fetcher.get_stock_info(stock2)
            
            st.success("✅ Pairs trading analysis completed!")
            
            # Display stock information
            st.subheader("📊 Stock Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### {stock1}")
                st.markdown(f"**Company:** {stock1_info.get('name', 'N/A')}")
                st.markdown(f"**Sector:** {stock1_info.get('sector', 'N/A')}")
                st.markdown(f"**Industry:** {stock1_info.get('industry', 'N/A')}")
                st.metric("Current Price", f"${stock1_info.get('price', 0):.2f}")
                if stock1_info.get('market_cap', 0) > 0:
                    market_cap = stock1_info['market_cap'] / 1e9
                    st.metric("Market Cap", f"${market_cap:.1f}B")
            
            with col2:
                st.markdown(f"### {stock2}")
                st.markdown(f"**Company:** {stock2_info.get('name', 'N/A')}")
                st.markdown(f"**Sector:** {stock2_info.get('sector', 'N/A')}")
                st.markdown(f"**Industry:** {stock2_info.get('industry', 'N/A')}")
                st.metric("Current Price", f"${stock2_info.get('price', 0):.2f}")
                if stock2_info.get('market_cap', 0) > 0:
                    market_cap = stock2_info['market_cap'] / 1e9
                    st.metric("Market Cap", f"${market_cap:.1f}B")
            
            st.markdown("---")
            
            # Perform cointegration test
            if show_cointegration:
                st.subheader("🔬 Cointegration Analysis")
                
                coint_result = pairs_analyzer.cointegration_test(stock1_prices, stock2_prices)
                
                if coint_result.get('cointegrated', False):
                    st.success("✅ Stocks are cointegrated - suitable for pairs trading!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Test Statistic", f"{coint_result['test_statistic']:.4f}")
                    
                    with col2:
                        st.metric("P-Value", f"{coint_result['p_value']:.6f}")
                    
                    with col3:
                        critical_5pct = coint_result['critical_values']['5%']
                        st.metric("Critical Value (5%)", f"{critical_5pct:.4f}")
                    
                    # Display interpretation
                    st.info(f"""
                    **Interpretation:** The Engle-Granger test indicates cointegration between {stock1} and {stock2}.
                    This suggests a long-term equilibrium relationship exists, making them suitable for pairs trading.
                    A p-value of {coint_result['p_value']:.6f} is below 0.05, rejecting the null hypothesis of no cointegration.
                    """)
                
                else:
                    st.warning("⚠️ Stocks are NOT cointegrated - pairs trading may not be effective")
                    
                    if 'error' in coint_result:
                        st.error(f"Error in cointegration test: {coint_result['error']}")
                    else:
                        st.info(f"""
                        **Interpretation:** The Engle-Granger test does not find evidence of cointegration.
                        P-value: {coint_result.get('p_value', 'N/A')}. Consider other pairs or different time periods.
                        """)
            
            # Calculate hedge ratio and spread
            st.subheader("📈 Hedge Ratio & Spread Analysis")
            
            hedge_result = pairs_analyzer.calculate_hedge_ratio(stock1_prices, stock2_prices)
            
            if 'error' not in hedge_result:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    hedge_ratio = hedge_result['hedge_ratio']
                    st.metric("Hedge Ratio", f"{hedge_ratio:.4f}")
                    st.caption(f"Long 1 share of {stock1}, Short {abs(hedge_ratio):.4f} shares of {stock2}")
                
                with col2:
                    r_squared = hedge_result['r_squared']
                    st.metric("R-Squared", f"{r_squared:.4f}")
                    st.caption("Regression fit quality")
                
                with col3:
                    t_stat = hedge_result['t_statistic']
                    st.metric("T-Statistic", f"{t_stat:.4f}")
                    st.caption("Statistical significance")
                
                # Calculate spread and z-score
                spread = pairs_analyzer.calculate_spread(stock1_prices, stock2_prices, hedge_ratio)
                zscore = pairs_analyzer.calculate_zscore(spread, lookback_window)
                
                # Current spread status
                if not zscore.empty:
                    current_zscore = zscore.iloc[-1]
                    st.subheader("🎯 Current Trading Signal")
                    
                    if abs(current_zscore) >= entry_threshold:
                        if current_zscore > 0:
                            signal_text = f"🔴 **SELL SIGNAL** - Z-score: {current_zscore:.2f}"
                            signal_interpretation = f"Short {stock1}, Long {stock2} (spread is overextended)"
                        else:
                            signal_text = f"🟢 **BUY SIGNAL** - Z-score: {current_zscore:.2f}"
                            signal_interpretation = f"Long {stock1}, Short {stock2} (spread is underextended)"
                        
                        st.markdown(signal_text)
                        st.caption(signal_interpretation)
                    
                    elif abs(current_zscore) <= exit_threshold:
                        st.info(f"🔵 **EXIT SIGNAL** - Z-score: {current_zscore:.2f} (close to equilibrium)")
                    
                    else:
                        st.info(f"⚪ **NO SIGNAL** - Z-score: {current_zscore:.2f} (waiting for entry threshold)")
            
            # Comprehensive pairs analysis plot
            st.subheader("📊 Comprehensive Pairs Analysis")
            
            pairs_fig = pairs_analyzer.plot_pairs_analysis(
                stock1_prices, stock2_prices, stock1, stock2
            )
            st.plotly_chart(pairs_fig, use_container_width=True)
            
            # Trading signals and backtest
            if show_trading_signals and 'error' not in hedge_result:
                st.subheader("🔄 Trading Signals Analysis")
                
                signals_result = pairs_analyzer.generate_trading_signals(
                    zscore, entry_threshold, exit_threshold
                )
                
                if 'signals' in signals_result:
                    signals_df = signals_result['signals']
                    
                    # Plot trading signals
                    fig_signals = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=['Z-Score and Trading Signals', 'Position History'],
                        vertical_spacing=0.1
                    )
                    
                    # Z-score plot
                    fig_signals.add_trace(go.Scatter(
                        x=signals_df.index,
                        y=signals_df['zscore'],
                        mode='lines',
                        name='Z-Score',
                        line=dict(color='blue')
                    ), row=1, col=1)
                    
                    # Entry/exit thresholds
                    fig_signals.add_hline(y=entry_threshold, line_dash="dash", line_color="red", row=1, col=1)
                    fig_signals.add_hline(y=-entry_threshold, line_dash="dash", line_color="red", row=1, col=1)
                    fig_signals.add_hline(y=exit_threshold, line_dash="dot", line_color="green", row=1, col=1)
                    fig_signals.add_hline(y=-exit_threshold, line_dash="dot", line_color="green", row=1, col=1)
                    fig_signals.add_hline(y=0, line_dash="solid", line_color="gray", row=1, col=1)
                    
                    # Long signals
                    long_signals = signals_df[signals_df['long_signal'] == 1]
                    if not long_signals.empty:
                        fig_signals.add_trace(go.Scatter(
                            x=long_signals.index,
                            y=long_signals['zscore'],
                            mode='markers',
                            name='Long Entry',
                            marker=dict(color='green', size=10, symbol='triangle-up')
                        ), row=1, col=1)
                    
                    # Short signals
                    short_signals = signals_df[signals_df['short_signal'] == 1]
                    if not short_signals.empty:
                        fig_signals.add_trace(go.Scatter(
                            x=short_signals.index,
                            y=short_signals['zscore'],
                            mode='markers',
                            name='Short Entry',
                            marker=dict(color='red', size=10, symbol='triangle-down')
                        ), row=1, col=1)
                    
                    # Position history
                    fig_signals.add_trace(go.Scatter(
                        x=signals_df.index,
                        y=signals_df['position'],
                        mode='lines+markers',
                        name='Position',
                        line=dict(color='purple'),
                        marker=dict(size=4)
                    ), row=2, col=1)
                    
                    fig_signals.update_layout(
                        title='Trading Signals and Position Management',
                        height=600,
                        showlegend=True
                    )
                    
                    fig_signals.update_yaxes(title_text="Z-Score", row=1, col=1)
                    fig_signals.update_yaxes(title_text="Position", row=2, col=1)
                    
                    st.plotly_chart(fig_signals, use_container_width=True)
                    
                    # Trading statistics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        n_trades = signals_result['n_trades']
                        st.metric("Number of Trades", f"{n_trades}")
                    
                    with col2:
                        total_return = signals_result['total_return']
                        st.metric("Total Return", f"{total_return:.4f}")
                    
                    with col3:
                        sharpe_ratio = signals_result['sharpe_ratio']
                        st.metric("Sharpe Ratio", f"{sharpe_ratio:.4f}")
                    
                    with col4:
                        win_rate = signals_result['win_rate'] * 100
                        st.metric("Win Rate", f"{win_rate:.1f}%")
            
            # Statistical tests
            st.subheader("📊 Statistical Analysis")
            
            # Test spread stationarity
            if 'error' not in hedge_result:
                spread = pairs_analyzer.calculate_spread(stock1_prices, stock2_prices, hedge_ratio)
                stationarity_result = pairs_analyzer.stationarity_test(spread)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Spread Stationarity Test (ADF)")
                    
                    if 'error' not in stationarity_result:
                        is_stationary = stationarity_result['is_stationary']
                        adf_pvalue = stationarity_result['p_value']
                        
                        if is_stationary:
                            st.success(f"✅ Spread is stationary (p-value: {adf_pvalue:.6f})")
                        else:
                            st.warning(f"⚠️ Spread may not be stationary (p-value: {adf_pvalue:.6f})")
                        
                        st.metric("ADF Statistic", f"{stationarity_result['adf_statistic']:.4f}")
                        st.metric("P-Value", f"{adf_pvalue:.6f}")
                    else:
                        st.error("Error in stationarity test")
                
                with col2:
                    st.markdown("#### Spread Statistics")
                    
                    st.metric("Mean Spread", f"{spread.mean():.4f}")
                    st.metric("Spread Std Dev", f"{spread.std():.4f}")
                    st.metric("Current Spread", f"{spread.iloc[-1]:.4f}")
                    
                    # Half-life calculation (approximate)
                    if not zscore.empty:
                        half_life_approx = -np.log(2) / np.log(1 - 1/lookback_window)
                        st.metric("Approx Half-Life", f"{half_life_approx:.1f} days")
            
            # Performance metrics comparison
            st.subheader("📈 Performance Comparison")
            
            # Calculate individual stock returns
            stock1_returns = stock1_prices.pct_change().dropna()
            stock2_returns = stock2_prices.pct_change().dropna()
            
            # Align returns
            aligned_returns = pd.concat([stock1_returns, stock2_returns], axis=1).dropna()
            aligned_returns.columns = [stock1, stock2]
            
            if len(aligned_returns) > 0:
                performance_data = []
                
                for symbol in [stock1, stock2]:
                    returns = aligned_returns[symbol]
                    annual_return = returns.mean() * 252 * 100
                    annual_vol = returns.std() * np.sqrt(252) * 100
                    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
                    
                    performance_data.append({
                        'Stock': symbol,
                        'Annual Return (%)': f"{annual_return:.2f}",
                        'Annual Volatility (%)': f"{annual_vol:.2f}",
                        'Sharpe Ratio': f"{sharpe:.4f}",
                        'Correlation': f"{aligned_returns[stock1].corr(aligned_returns[stock2]):.4f}" if symbol == stock1 else "-"
                    })
                
                # Add pairs strategy performance if available
                if 'signals' in locals() and 'signals_result' in locals():
                    strategy_return = signals_result['total_return'] * 100
                    strategy_sharpe = signals_result['sharpe_ratio']
                    
                    performance_data.append({
                        'Stock': 'Pairs Strategy',
                        'Annual Return (%)': f"{strategy_return:.2f}",
                        'Annual Volatility (%)': "-",
                        'Sharpe Ratio': f"{strategy_sharpe:.4f}",
                        'Correlation': "-"
                    })
                
                performance_df = pd.DataFrame(performance_data)
                st.dataframe(performance_df, use_container_width=True)
                
                # Correlation over time
                st.subheader("🔗 Rolling Correlation Analysis")
                
                correlation_window = 60  # 60-day rolling correlation
                rolling_corr = aligned_returns[stock1].rolling(correlation_window).corr(aligned_returns[stock2])
                
                fig_corr = go.Figure()
                fig_corr.add_trace(go.Scatter(
                    x=rolling_corr.index,
                    y=rolling_corr.values,
                    mode='lines',
                    name=f'{correlation_window}-Day Rolling Correlation',
                    line=dict(color='purple', width=2)
                ))
                
                # Add mean correlation line
                mean_corr = rolling_corr.mean()
                fig_corr.add_hline(
                    y=mean_corr,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Mean: {mean_corr:.3f}"
                )
                
                fig_corr.update_layout(
                    title=f'Rolling Correlation: {stock1} vs {stock2}',
                    xaxis_title='Date',
                    yaxis_title='Correlation',
                    yaxis=dict(range=[-1, 1])
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
            
            # Summary and recommendations
            st.subheader("📋 Analysis Summary & Recommendations")
            
            summary_data = pairs_analyzer.pairs_summary_table(stock1_prices, stock2_prices)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Key Metrics")
                
                if summary_data.get('cointegrated', False):
                    st.success("✅ Pair is suitable for trading")
                    st.metric("Cointegration P-Value", f"{summary_data.get('cointegration_p_value', 0):.6f}")
                    st.metric("Hedge Ratio", f"{summary_data.get('hedge_ratio', 0):.4f}")
                    st.metric("R-Squared", f"{summary_data.get('r_squared', 0):.4f}")
                else:
                    st.warning("⚠️ Pair may not be suitable")
                    st.metric("Cointegration P-Value", f"{summary_data.get('cointegration_p_value', 1):.6f}")
            
            with col2:
                st.markdown("#### Trading Recommendations")
                
                if summary_data.get('cointegrated', False):
                    if summary_data.get('r_squared', 0) > 0.7:
                        st.success("Strong relationship - Good for trading")
                    elif summary_data.get('r_squared', 0) > 0.5:
                        st.info("Moderate relationship - Consider with caution")
                    else:
                        st.warning("Weak relationship - High risk")
                    
                    if summary_data.get('spread_is_stationary', False):
                        st.success("Spread is stationary - Good mean reversion")
                    else:
                        st.warning("Spread may not be stationary")
                else:
                    st.error("Not recommended for pairs trading")
            
            # Export functionality
            st.subheader("📄 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Export Data to CSV"):
                    csv_data = {
                        'pair_info': pd.DataFrame([{
                            'Stock1': stock1,
                            'Stock2': stock2,
                            'Analysis_Period': period,
                            'Cointegrated': summary_data.get('cointegrated', False),
                            'Hedge_Ratio': summary_data.get('hedge_ratio', np.nan),
                            'R_Squared': summary_data.get('r_squared', np.nan)
                        }]),
                        'stock1_prices': pd.DataFrame({'Date': stock1_prices.index, 'Price': stock1_prices.values}),
                        'stock2_prices': pd.DataFrame({'Date': stock2_prices.index, 'Price': stock2_prices.values}),
                        'performance_comparison': performance_df if 'performance_df' in locals() else pd.DataFrame()
                    }
                    
                    if 'spread' in locals():
                        csv_data['spread_analysis'] = pd.DataFrame({
                            'Date': spread.index,
                            'Spread': spread.values
                        })
                    
                    if 'zscore' in locals() and not zscore.empty:
                        csv_data['zscore_analysis'] = pd.DataFrame({
                            'Date': zscore.index,
                            'ZScore': zscore.values
                        })
                    
                    if 'signals_df' in locals():
                        csv_data['trading_signals'] = signals_df
                    
                    csv_files = report_generator.export_data_to_csv(csv_data, "pairs_trading")
                    
                    for filename, csv_bytes in csv_files.items():
                        st.download_button(
                            label=f"⬇️ Download {filename}",
                            data=csv_bytes,
                            file_name=filename,
                            mime="text/csv"
                        )
            
            with col2:
                st.info("PDF report generation can be added for detailed pairs analysis")
    
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        st.exception(e)

else:
    # Initial instructions
    st.info("""
    ## 🚀 Getting Started with Pairs Trading
    
    1. **Select Asset Pair**: Choose two stocks to analyze for pairs trading
    2. **Set Time Period**: Select historical period for cointegration analysis
    3. **Configure Parameters**: Set lookback window and entry/exit thresholds
    4. **Run Analysis**: Click "Analyze Pair" to perform comprehensive analysis
    
    ### 🔄 Pairs Trading Concepts
    
    #### 📊 Statistical Arbitrage
    Pairs trading is a market-neutral strategy that profits from temporary divergences 
    between historically correlated securities. The strategy assumes that price relationships 
    will revert to their long-term equilibrium.
    
    #### 🔬 Cointegration Testing
    - **Engle-Granger Test**: Tests for long-term equilibrium relationship
    - **P-Value < 0.05**: Indicates cointegration (suitable for pairs trading)
    - **Test Statistic**: Compared against critical values
    
    #### 📈 Hedge Ratio Calculation
    - **OLS Regression**: Determines optimal hedge ratio between assets
    - **R-Squared**: Measures strength of linear relationship
    - **T-Statistic**: Statistical significance of the relationship
    
    #### 📊 Spread Analysis
    - **Price Spread**: Difference between hedged positions
    - **Z-Score**: Standardized measure of spread deviation
    - **Mean Reversion**: Assumption that spread returns to historical mean
    
    ### 🎯 Trading Strategy
    
    #### 🔴 Entry Signals
    - **Long Signal**: Z-score < -2.0 (buy underperforming stock, short outperforming)
    - **Short Signal**: Z-score > +2.0 (short underperforming stock, buy outperforming)
    
    #### 🟢 Exit Signals
    - **Position Close**: Z-score approaches 0 (spread reverts to mean)
    - **Stop Loss**: Z-score continues to diverge beyond limits
    
    ### 🔗 Popular Pairs by Sector
    - **Technology**: AAPL/MSFT, GOOGL/META, NVDA/AMD
    - **Banking**: JPM/BAC, WFC/C, GS/MS
    - **Energy**: XOM/CVX, COP/EOG
    - **Retail**: WMT/TGT, HD/LOW
    - **Healthcare**: JNJ/PFE, UNH/CVS
    
    ### ⚠️ Risk Considerations
    - **Cointegration Breakdown**: Relationships can change over time
    - **Market Stress**: Correlations may fail during crisis periods
    - **Sector Risk**: Both stocks may decline together
    - **Execution Risk**: Timing and slippage in trade execution
    
    ### 📈 Performance Metrics
    - **Sharpe Ratio**: Risk-adjusted returns of the strategy
    - **Win Rate**: Percentage of profitable trades
    - **Maximum Drawdown**: Largest peak-to-trough decline
    - **Half-Life**: Average time for spread to revert to mean
    """)
    
    # Show example pair analysis
    if st.button("📊 View Sample Analysis"):
        st.markdown("### Sample Pairs Trading Concept")
        
        # Create sample visualization
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Generate correlated price series
        stock_a = 100 + np.cumsum(np.random.normal(0.001, 0.02, len(dates)))
        stock_b = 50 + np.cumsum(np.random.normal(0.0008, 0.015, len(dates))) + 0.3 * (stock_a - 100)
        
        # Calculate spread and z-score
        hedge_ratio = 0.5
        spread = stock_a - hedge_ratio * stock_b
        zscore = (spread - spread.mean()) / spread.std()
        
        # Create visualization
        fig_sample = make_subplots(
            rows=3, cols=1,
            subplot_titles=['Normalized Stock Prices', 'Price Spread', 'Z-Score and Trading Signals'],
            vertical_spacing=0.1
        )
        
        # Normalized prices
        fig_sample.add_trace(go.Scatter(
            x=dates, y=stock_a/stock_a[0]*100,
            mode='lines', name='Stock A', line=dict(color='blue')
        ), row=1, col=1)
        
        fig_sample.add_trace(go.Scatter(
            x=dates, y=stock_b/stock_b[0]*100,
            mode='lines', name='Stock B', line=dict(color='red')
        ), row=1, col=1)
        
        # Spread
        fig_sample.add_trace(go.Scatter(
            x=dates, y=spread,
            mode='lines', name='Spread', line=dict(color='purple')
        ), row=2, col=1)
        
        # Z-score with trading signals
        fig_sample.add_trace(go.Scatter(
            x=dates, y=zscore,
            mode='lines', name='Z-Score', line=dict(color='green')
        ), row=3, col=1)
        
        # Add trading thresholds
        fig_sample.add_hline(y=2, line_dash="dash", line_color="red", row=3, col=1)
        fig_sample.add_hline(y=-2, line_dash="dash", line_color="red", row=3, col=1)
        fig_sample.add_hline(y=0, line_dash="solid", line_color="gray", row=3, col=1)
        
        fig_sample.update_layout(
            title='Sample Pairs Trading Analysis',
            height=800,
            showlegend=True
        )
        
        st.plotly_chart(fig_sample, use_container_width=True)
        
        st.caption("This is a sample visualization showing pairs trading concepts. Use real market data for actual analysis.")
        
        # Sample statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            correlation = np.corrcoef(stock_a, stock_b)[0,1]
            st.metric("Correlation", f"{correlation:.3f}")
        
        with col2:
            st.metric("Hedge Ratio", f"{hedge_ratio:.3f}")
        
        with col3:
            current_zscore = zscore[-1]
            st.metric("Current Z-Score", f"{current_zscore:.2f}")
        
        with col4:
            trading_signals = len(zscore[np.abs(zscore) > 2])
            st.metric("Trading Signals", f"{trading_signals}")
