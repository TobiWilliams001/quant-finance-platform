import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantrisk.data.fetcher import DataFetcher
from quantrisk.analytics.risk import RiskAnalytics
from quantrisk.utils.reports import ReportGenerator
from quantrisk.data.database import get_db_manager

# Configure page
st.set_page_config(
    page_title="Risk Analytics",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ Risk Analytics")
st.markdown("---")

# Initialize classes
data_fetcher = DataFetcher()
risk_analyzer = RiskAnalytics()
report_generator = ReportGenerator()
db_manager = get_db_manager()

# Sidebar for parameters
st.sidebar.title("📊 Risk Analysis Parameters")

# Database status indicator
if db_manager.initialized:
    st.sidebar.success("🗄️ Database: Connected")
else:
    st.sidebar.warning("🗄️ Database: Offline")

# Check for sample analysis setup
use_sample_data = st.session_state.get('run_sample_analysis', False)

# Portfolio selection
st.sidebar.subheader("Portfolio Selection")
if use_sample_data and 'sample_symbols' in st.session_state:
    default_symbols = '\n'.join(st.session_state.sample_symbols)
else:
    default_symbols = "AAPL\nGOOGL\nMSFT\nTSLA\nAMZN"

symbols_input = st.sidebar.text_area(
    "Enter stock symbols (one per line)",
    value=default_symbols,
    height=120,
    help="Enter stock symbols separated by new lines"
)

symbols = [symbol.strip().upper() for symbol in symbols_input.strip().split('\n') if symbol.strip()]

# Time period
if use_sample_data and 'sample_period' in st.session_state:
    default_period_index = ["1y", "2y", "3y", "5y", "max"].index(st.session_state.sample_period)
else:
    default_period_index = 0
    
period = st.sidebar.selectbox(
    "Analysis Period",
    ["1y", "2y", "3y", "5y", "max"],
    index=default_period_index,
    help="Time period for historical data analysis"
)

# Portfolio weights
st.sidebar.subheader("Portfolio Weights")
equal_weights = st.sidebar.checkbox("Equal Weights", value=True)

weights = {}
if not equal_weights and symbols:
    for symbol in symbols:
        weights[symbol] = st.sidebar.number_input(
            f"{symbol} Weight",
            min_value=0.0,
            max_value=1.0,
            value=1.0/len(symbols),
            step=0.01,
            format="%.3f"
        )
    
    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v/total_weight for k, v in weights.items()}
else:
    weights = {symbol: 1.0/len(symbols) for symbol in symbols}

# Risk parameters
st.sidebar.subheader("Risk Parameters")
if use_sample_data and 'sample_confidence' in st.session_state:
    default_confidence = st.session_state.sample_confidence
else:
    default_confidence = [0.95, 0.99]
    
confidence_levels = st.sidebar.multiselect(
    "VaR Confidence Levels",
    [0.90, 0.95, 0.99],
    default=default_confidence
)

if use_sample_data and 'sample_risk_free_rate' in st.session_state:
    default_risk_free = st.session_state.sample_risk_free_rate * 100
else:
    default_risk_free = 2.0
    
risk_free_rate = st.sidebar.number_input(
    "Risk-Free Rate (%)",
    min_value=0.0,
    max_value=10.0,
    value=default_risk_free,
    step=0.1,
    format="%.2f"
) / 100

# Benchmark selection
if use_sample_data and 'sample_benchmark' in st.session_state:
    benchmark_options = ["None", "^GSPC", "^IXIC", "^DJI", "^TNX"]
    default_benchmark_index = benchmark_options.index(st.session_state.sample_benchmark) if st.session_state.sample_benchmark in benchmark_options else 1
else:
    default_benchmark_index = 1
    
benchmark_symbol = st.sidebar.selectbox(
    "Benchmark (optional)",
    ["None", "^GSPC", "^IXIC", "^DJI", "^TNX"],
    index=default_benchmark_index,
    help="Select a benchmark for comparison"
)

# Analysis button
run_analysis = st.sidebar.button("🔍 Run Risk Analysis", type="primary")

# Auto-run for sample analysis or manual trigger
should_run_analysis = (run_analysis and symbols) or (use_sample_data and symbols)

if should_run_analysis:
    # Clear sample analysis flag to prevent auto-rerun
    if 'run_sample_analysis' in st.session_state:
        del st.session_state.run_sample_analysis
    try:
        with st.spinner("Fetching market data and performing risk analysis..."):
            # Validate symbols
            valid_symbols = data_fetcher.validate_symbols(symbols)
            
            if not valid_symbols:
                st.error("No valid symbols found. Please check your input.")
                st.stop()
            
            if len(valid_symbols) != len(symbols):
                st.warning(f"Some symbols were invalid. Proceeding with: {', '.join(valid_symbols)}")
                symbols = valid_symbols
                # Recalculate weights for valid symbols only
                weights = {symbol: 1.0/len(symbols) for symbol in symbols}
            
            # Fetch data
            returns_data = data_fetcher.get_returns_matrix(symbols, period)
            
            if returns_data.empty:
                st.error("Unable to fetch sufficient data for analysis.")
                st.stop()
            
            # Calculate portfolio returns
            portfolio_weights = np.array([weights.get(symbol, 0) for symbol in returns_data.columns])
            portfolio_returns = (returns_data * portfolio_weights).sum(axis=1)
            
            # Calculate portfolio prices (assuming $10,000 initial investment)
            initial_value = 10000
            portfolio_prices = (1 + portfolio_returns).cumprod() * initial_value
            
            # Fetch benchmark data if selected
            benchmark_returns = None
            if benchmark_symbol != "None":
                try:
                    with st.spinner(f"Fetching benchmark data ({benchmark_symbol})..."):
                        benchmark_data = data_fetcher.fetch_stock_data(benchmark_symbol, period)
                        
                    if not benchmark_data.empty and len(benchmark_data) > 10:
                        benchmark_returns = benchmark_data['Close'].pct_change().dropna()
                        
                        # Ensure we have enough data points
                        if len(benchmark_returns) > 10:
                            # Align with portfolio returns
                            aligned_data = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
                            if len(aligned_data) > 10:
                                portfolio_returns = aligned_data.iloc[:, 0]
                                benchmark_returns = aligned_data.iloc[:, 1]
                                # Recalculate portfolio prices
                                portfolio_prices = (1 + portfolio_returns).cumprod() * initial_value
                                st.success(f"✅ Benchmark data ({benchmark_symbol}) loaded successfully!")
                            else:
                                benchmark_returns = None
                                st.warning(f"⚠️ Insufficient overlapping data between portfolio and benchmark ({benchmark_symbol}). Proceeding without benchmark comparison.")
                        else:
                            benchmark_returns = None
                            st.warning(f"⚠️ Insufficient benchmark data points for {benchmark_symbol}. Proceeding without benchmark comparison.")
                    else:
                        benchmark_returns = None
                        st.warning(f"⚠️ Unable to fetch sufficient benchmark data for {benchmark_symbol}. Proceeding without benchmark comparison.")
                        
                except Exception as e:
                    benchmark_returns = None
                    st.warning(f"⚠️ Error fetching benchmark data for {benchmark_symbol}: {str(e)}. Proceeding without benchmark comparison.")
            
            # Perform comprehensive risk analysis
            risk_report = risk_analyzer.comprehensive_risk_report(
                returns=portfolio_returns,
                prices=portfolio_prices,
                benchmark_returns=benchmark_returns,
                risk_free_rate=risk_free_rate
            )
            
            # Save analysis results to database
            if db_manager.initialized:
                try:
                    # Prepare analysis parameters
                    analysis_params = {
                        'symbols': symbols,
                        'period': period,
                        'weights': weights,
                        'confidence_levels': confidence_levels,
                        'risk_free_rate': risk_free_rate,
                        'benchmark': benchmark_symbol,
                        'equal_weights': equal_weights
                    }
                    
                    # Save analysis history
                    db_manager.save_analysis_history(
                        analysis_type='risk',
                        symbols=symbols,
                        parameters=analysis_params,
                        results=risk_report,
                        success=True
                    )
                    
                    # Save portfolio snapshot
                    portfolio_name = f"Risk Analysis - {', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''}"
                    db_manager.save_portfolio_snapshot(
                        portfolio_name=portfolio_name,
                        symbols=symbols,
                        weights=weights,
                        returns_data=returns_data,
                        risk_metrics=risk_report,
                        benchmark=benchmark_symbol if benchmark_symbol != "None" else None,
                        period=period
                    )
                    
                    st.success("✅ Risk analysis completed and saved to database!")
                    
                except Exception as db_error:
                    st.warning(f"⚠️ Analysis completed but database save failed: {str(db_error)}")
                    st.success("✅ Risk analysis completed successfully!")
            else:
                st.success("✅ Risk analysis completed successfully!")
                st.info("💡 Enable database features to save analysis history")
            
            # Key metrics overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                annual_return = risk_report['returns_mean'] * 100
                st.metric(
                    "Annual Return",
                    f"{annual_return:.2f}%",
                    delta=None
                )
            
            with col2:
                annual_vol = risk_report['returns_std'] * 100
                st.metric(
                    "Annual Volatility",
                    f"{annual_vol:.2f}%",
                    delta=None
                )
            
            with col3:
                sharpe = risk_report['sharpe_ratio']
                st.metric(
                    "Sharpe Ratio",
                    f"{sharpe:.3f}",
                    delta=None
                )
            
            with col4:
                max_dd = abs(risk_report['max_drawdown']) * 100
                st.metric(
                    "Max Drawdown",
                    f"{max_dd:.2f}%",
                    delta=None
                )
            
            st.markdown("---")
            
            # Portfolio performance chart
            st.subheader("📈 Portfolio Performance")
            
            fig_performance = go.Figure()
            
            # Portfolio cumulative returns
            cumulative_returns = (1 + portfolio_returns).cumprod()
            fig_performance.add_trace(go.Scatter(
                x=portfolio_returns.index,
                y=cumulative_returns * 100,
                mode='lines',
                name='Portfolio',
                line=dict(color='blue', width=2)
            ))
            
            # Benchmark comparison
            if benchmark_returns is not None:
                benchmark_cumulative = (1 + benchmark_returns).cumprod()
                fig_performance.add_trace(go.Scatter(
                    x=benchmark_returns.index,
                    y=benchmark_cumulative * 100,
                    mode='lines',
                    name=f'Benchmark ({benchmark_symbol})',
                    line=dict(color='red', width=2)
                ))
            
            fig_performance.update_layout(
                title='Cumulative Returns Comparison',
                xaxis_title='Date',
                yaxis_title='Cumulative Return (%)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_performance, use_container_width=True)
            
            # Drawdown analysis
            st.subheader("📉 Drawdown Analysis")
            
            drawdown_series = risk_report['drawdown_series'] * 100
            
            fig_drawdown = go.Figure()
            fig_drawdown.add_trace(go.Scatter(
                x=drawdown_series.index,
                y=drawdown_series.values,
                mode='lines',
                fill='tonexty',
                name='Drawdown',
                line=dict(color='red'),
                fillcolor='rgba(255, 0, 0, 0.3)'
            ))
            
            fig_drawdown.update_layout(
                title='Portfolio Drawdown Over Time',
                xaxis_title='Date',
                yaxis_title='Drawdown (%)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_drawdown, use_container_width=True)
            
            # VaR and CVaR analysis
            st.subheader("⚠️ Value at Risk Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Value at Risk (VaR)**")
                var_results = risk_report['var']
                for confidence in confidence_levels:
                    if confidence in var_results:
                        var_value = abs(var_results[confidence]) * 100
                        st.metric(
                            f"VaR ({confidence*100:.0f}%)",
                            f"{var_value:.2f}%"
                        )
            
            with col2:
                st.markdown("**Conditional Value at Risk (CVaR)**")
                cvar_results = risk_report['cvar']
                for confidence in confidence_levels:
                    if confidence in cvar_results:
                        cvar_value = abs(cvar_results[confidence]) * 100
                        st.metric(
                            f"CVaR ({confidence*100:.0f}%)",
                            f"{cvar_value:.2f}%"
                        )
            
            # Return distribution analysis
            st.subheader("📊 Return Distribution Analysis")
            
            # Histogram of returns
            fig_dist = make_subplots(
                rows=1, cols=2,
                subplot_titles=['Return Distribution', 'Q-Q Plot vs Normal Distribution']
            )
            
            # Histogram
            fig_dist.add_trace(go.Histogram(
                x=portfolio_returns * 100,
                nbinsx=50,
                name='Portfolio Returns',
                histnorm='probability density'
            ), row=1, col=1)
            
            # Normal distribution overlay
            returns_mean = portfolio_returns.mean() * 100
            returns_std = portfolio_returns.std() * 100
            x_range = np.linspace(portfolio_returns.min() * 100, portfolio_returns.max() * 100, 100)
            normal_dist = (1 / (returns_std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - returns_mean) / returns_std) ** 2)
            
            fig_dist.add_trace(go.Scatter(
                x=x_range,
                y=normal_dist,
                mode='lines',
                name='Normal Distribution',
                line=dict(color='red', width=2)
            ), row=1, col=1)
            
            # Q-Q plot
            from scipy import stats
            sorted_returns = np.sort(portfolio_returns * 100)
            theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(sorted_returns)))
            theoretical_quantiles = theoretical_quantiles * returns_std + returns_mean
            
            fig_dist.add_trace(go.Scatter(
                x=theoretical_quantiles,
                y=sorted_returns,
                mode='markers',
                name='Actual vs Normal',
                marker=dict(size=4)
            ), row=1, col=2)
            
            # Perfect normal line
            min_val = min(theoretical_quantiles.min(), sorted_returns.min())
            max_val = max(theoretical_quantiles.max(), sorted_returns.max())
            fig_dist.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Perfect Normal',
                line=dict(color='red', dash='dash')
            ), row=1, col=2)
            
            fig_dist.update_layout(
                title='Portfolio Return Distribution Analysis',
                height=400
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Distribution statistics
            st.subheader("📈 Distribution Statistics")
            
            dist_stats = risk_report['distribution']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Skewness", f"{dist_stats['skewness']:.4f}")
                st.caption("Measure of asymmetry")
            
            with col2:
                st.metric("Kurtosis", f"{dist_stats['kurtosis']:.4f}")
                st.caption("Measure of tail heaviness")
            
            with col3:
                jb_stat = dist_stats['jarque_bera_stat']
                st.metric("Jarque-Bera", f"{jb_stat:.4f}")
                st.caption("Normality test statistic")
            
            with col4:
                jb_pvalue = dist_stats['jarque_bera_pvalue']
                st.metric("JB P-Value", f"{jb_pvalue:.6f}")
                st.caption("Normality test p-value")
            
            # Benchmark comparison metrics
            if benchmark_returns is not None:
                st.subheader("🔄 Benchmark Comparison")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    beta = risk_report.get('beta', 0)
                    st.metric("Beta", f"{beta:.4f}")
                    st.caption("Systematic risk measure")
                
                with col2:
                    tracking_error = risk_report.get('tracking_error', 0) * 100
                    st.metric("Tracking Error", f"{tracking_error:.2f}%")
                    st.caption("Standard deviation of excess returns")
                
                with col3:
                    info_ratio = risk_report.get('information_ratio', 0)
                    st.metric("Information Ratio", f"{info_ratio:.4f}")
                    st.caption("Risk-adjusted excess return")
            
            # Portfolio composition
            st.subheader("💼 Portfolio Composition")
            
            # Pie chart of portfolio weights
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(weights.keys()),
                values=list(weights.values()),
                hole=0.3,
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig_pie.update_layout(
                title='Portfolio Allocation',
                height=400
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Export functionality
            st.subheader("📄 Export Results")
            
            # Initialize session state for exports
            if 'pdf_generated' not in st.session_state:
                st.session_state.pdf_generated = False
            if 'csv_generated' not in st.session_state:
                st.session_state.csv_generated = False
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate PDF button
                if st.button("📋 Generate PDF Report", key="generate_pdf_btn"):
                    with st.spinner("Generating PDF report..."):
                        try:
                            portfolio_name = f"Portfolio ({', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''})"
                            st.session_state.pdf_bytes = report_generator.generate_risk_analytics_report(
                                risk_report, portfolio_name
                            )
                            st.session_state.pdf_filename = f"risk_analytics_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            st.session_state.pdf_generated = True
                            st.success("✅ PDF report generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
                
                # Show download button if PDF is generated
                if st.session_state.pdf_generated and hasattr(st.session_state, 'pdf_bytes'):
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=st.session_state.pdf_bytes,
                        file_name=st.session_state.pdf_filename,
                        mime="application/pdf",
                        key="download_pdf_btn"
                    )
            
            with col2:
                # Generate CSV button
                if st.button("📊 Export Data to CSV", key="generate_csv_btn"):
                    with st.spinner("Preparing CSV export..."):
                        try:
                            csv_data = {
                                'portfolio_returns': pd.DataFrame({'date': portfolio_returns.index, 'returns': portfolio_returns.values}),
                                'portfolio_prices': pd.DataFrame({'date': portfolio_prices.index, 'prices': portfolio_prices.values}),
                                'weights': pd.DataFrame(list(weights.items()), columns=['Symbol', 'Weight'])
                            }
                            
                            if benchmark_returns is not None:
                                csv_data['benchmark_returns'] = pd.DataFrame({'date': benchmark_returns.index, 'benchmark_returns': benchmark_returns.values})
                            
                            st.session_state.csv_files = report_generator.export_data_to_csv(csv_data, "risk_analytics")
                            st.session_state.csv_generated = True
                            st.success("✅ CSV files generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating CSV: {str(e)}")
                
                # Show download buttons if CSV is generated
                if st.session_state.csv_generated and hasattr(st.session_state, 'csv_files'):
                    for i, (filename, csv_bytes) in enumerate(st.session_state.csv_files.items()):
                        display_name = filename.split('_')[2:-2]  # Extract meaningful part of filename
                        display_name = ' '.join(display_name).title() if display_name else filename
                        st.download_button(
                            label=f"⬇️ Download {display_name}",
                            data=csv_bytes,
                            file_name=filename,
                            mime="text/csv",
                            key=f"download_csv_btn_{i}"
                        )
    
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        st.exception(e)

else:
    # Initial instructions
    st.info("""
    ## 🚀 Getting Started with Risk Analytics
    
    1. **Select Your Portfolio**: Enter stock symbols in the sidebar (one per line)
    2. **Choose Time Period**: Select the analysis period for historical data
    3. **Set Portfolio Weights**: Use equal weights or specify custom allocations
    4. **Configure Risk Parameters**: Set VaR confidence levels and risk-free rate
    5. **Select Benchmark**: Choose a benchmark for comparison (optional)
    6. **Run Analysis**: Click "Run Risk Analysis" to generate comprehensive risk metrics
    
    ### 📊 Analysis Features
    - **Value at Risk (VaR)** calculation at multiple confidence levels
    - **Conditional VaR** for tail risk assessment
    - **Maximum Drawdown** analysis with time series visualization
    - **Sharpe and Sortino Ratios** for risk-adjusted performance
    - **Distribution Analysis** including skewness, kurtosis, and normality tests
    - **Benchmark Comparison** with beta, tracking error, and information ratio
    - **Professional PDF Reports** and CSV data exports
    
    ### ⚠️ Risk Interpretation Guide
    - **VaR**: Maximum expected loss at given confidence level
    - **CVaR**: Expected loss beyond VaR threshold (tail risk)
    - **Sharpe Ratio**: Higher values indicate better risk-adjusted returns
    - **Max Drawdown**: Largest peak-to-trough decline
    - **Beta**: Sensitivity to market movements (>1 = more volatile than market)
    - **Skewness**: Negative values indicate more downside risk
    - **Kurtosis**: Higher values indicate more extreme outliers
    """)
    
    # Sample analysis example
    if st.button("🔬 Try Sample Analysis"):
        # Set up sample data in session state
        st.session_state.sample_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
        st.session_state.sample_period = "2y"
        st.session_state.sample_confidence = [0.95, 0.99]
        st.session_state.sample_risk_free_rate = 0.025
        st.session_state.sample_benchmark = "^GSPC"
        st.session_state.run_sample_analysis = True
        st.rerun()
