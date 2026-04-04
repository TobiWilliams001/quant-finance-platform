import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from quantrisk.analytics.portfolio import PortfolioOptimizer
from quantrisk.analytics.risk import RiskAnalytics
from quantrisk.data.fetcher import DataFetcher
from quantrisk.utils.reports import ReportGenerator

# Configure page
st.set_page_config(page_title="Portfolio Optimization", page_icon="📊", layout="wide")

st.title("📊 Portfolio Optimization")
st.markdown("---")

# Initialize classes
data_fetcher = DataFetcher()
risk_analyzer = RiskAnalytics()
report_generator = ReportGenerator()

# Sidebar for parameters
st.sidebar.title("⚙️ Optimization Parameters")

# Asset selection
st.sidebar.subheader("Asset Universe")
symbols_input = st.sidebar.text_area(
    "Enter asset symbols (one per line)",
    value="AAPL\nGOOGL\nMSFT\nTSLA\nAMZN\nJPM\nJNJ\nPG\nXOM\nVZ",
    height=150,
    help="Enter stock symbols separated by new lines",
)

symbols = [
    symbol.strip().upper()
    for symbol in symbols_input.strip().split("\n")
    if symbol.strip()
]

# Time period
period = st.sidebar.selectbox(
    "Historical Data Period",
    ["1y", "2y", "3y", "5y"],
    index=1,
    help="Time period for calculating expected returns and covariance",
)

# Risk-free rate
risk_free_rate = (
    st.sidebar.number_input(
        "Risk-Free Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
        format="%.2f",
    )
    / 100
)

# Optimization constraints
st.sidebar.subheader("Constraints")

min_weight = (
    st.sidebar.number_input(
        "Minimum Weight per Asset (%)",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=1.0,
        format="%.1f",
    )
    / 100
)

max_weight = (
    st.sidebar.number_input(
        "Maximum Weight per Asset (%)",
        min_value=1.0,
        max_value=100.0,
        value=100.0,
        step=1.0,
        format="%.1f",
    )
    / 100
)

# Optimization settings
st.sidebar.subheader("Optimization Settings")

num_frontier_points = st.sidebar.slider(
    "Efficient Frontier Points",
    min_value=20,
    max_value=200,
    value=100,
    step=10,
    help="Number of portfolios to generate for efficient frontier",
)

# Optimization button
run_optimization = st.sidebar.button("🎯 Optimize Portfolio", type="primary")

if run_optimization and symbols:
    try:
        with st.spinner("Fetching data and optimizing portfolio..."):
            # Validate symbols
            valid_symbols = data_fetcher.validate_symbols(symbols)

            if len(valid_symbols) < 2:
                st.error(
                    "At least 2 valid symbols are required for portfolio optimization."
                )
                st.stop()

            if len(valid_symbols) != len(symbols):
                st.warning(
                    f"Some symbols were invalid. Proceeding with: {', '.join(valid_symbols)}"
                )
                symbols = valid_symbols

            # Fetch returns data
            returns_data = data_fetcher.get_returns_matrix(symbols, period)

            if returns_data.empty or len(returns_data) < 50:
                st.error(
                    "Insufficient data for optimization. Need at least 50 observations."
                )
                st.stop()

            # Initialize portfolio optimizer
            optimizer = PortfolioOptimizer(returns_data, risk_free_rate)

            # Perform optimizations
            max_sharpe_portfolio = optimizer.optimize_sharpe()
            min_vol_portfolio = optimizer.optimize_minimum_variance()

            if not max_sharpe_portfolio["success"] or not min_vol_portfolio["success"]:
                st.error("Optimization failed. Please check your data and constraints.")
                st.stop()

            # Generate efficient frontier
            frontier_data = optimizer.efficient_frontier(num_frontier_points)

            st.success("✅ Portfolio optimization completed successfully!")

            # Key results overview
            st.subheader("🎯 Optimization Results")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📈 Maximum Sharpe Ratio Portfolio")
                sharpe_metrics = max_sharpe_portfolio

                st.metric(
                    "Expected Return", f"{sharpe_metrics['expected_return']*100:.2f}%"
                )
                st.metric("Volatility", f"{sharpe_metrics['volatility']*100:.2f}%")
                st.metric("Sharpe Ratio", f"{sharpe_metrics['sharpe_ratio']:.4f}")

            with col2:
                st.markdown("### 🛡️ Minimum Volatility Portfolio")
                min_vol_metrics = min_vol_portfolio

                st.metric(
                    "Expected Return", f"{min_vol_metrics['expected_return']*100:.2f}%"
                )
                st.metric("Volatility", f"{min_vol_metrics['volatility']*100:.2f}%")
                st.metric("Sharpe Ratio", f"{min_vol_metrics['sharpe_ratio']:.4f}")

            st.markdown("---")

            # Efficient Frontier Plot
            st.subheader("📊 Efficient Frontier")

            efficient_frontier_fig = optimizer.plot_efficient_frontier(frontier_data)
            st.plotly_chart(efficient_frontier_fig, use_container_width=True)

            # Portfolio compositions
            st.subheader("💼 Portfolio Compositions")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Maximum Sharpe Ratio Portfolio")
                max_sharpe_pie = optimizer.portfolio_composition_pie(
                    max_sharpe_portfolio["weights"], symbols
                )
                st.plotly_chart(max_sharpe_pie, use_container_width=True)

                # Detailed weights table
                weights_df = pd.DataFrame(
                    {
                        "Asset": symbols,
                        "Weight (%)": max_sharpe_portfolio["weights"] * 100,
                    }
                ).round(2)
                weights_df = weights_df[weights_df["Weight (%)"] > 0.1].sort_values(
                    "Weight (%)", ascending=False
                )
                st.dataframe(weights_df, use_container_width=True)

            with col2:
                st.markdown("#### Minimum Volatility Portfolio")
                min_vol_pie = optimizer.portfolio_composition_pie(
                    min_vol_portfolio["weights"], symbols
                )
                st.plotly_chart(min_vol_pie, use_container_width=True)

                # Detailed weights table
                weights_df_min = pd.DataFrame(
                    {"Asset": symbols, "Weight (%)": min_vol_portfolio["weights"] * 100}
                ).round(2)
                weights_df_min = weights_df_min[
                    weights_df_min["Weight (%)"] > 0.1
                ].sort_values("Weight (%)", ascending=False)
                st.dataframe(weights_df_min, use_container_width=True)

            # Asset correlation analysis
            st.subheader("🔗 Asset Correlation Analysis")

            correlation_heatmap = optimizer.correlation_heatmap()
            st.plotly_chart(correlation_heatmap, use_container_width=True)

            # Individual asset analysis
            st.subheader("📈 Individual Asset Analysis")

            risk_return_scatter = optimizer.risk_return_scatter()
            st.plotly_chart(risk_return_scatter, use_container_width=True)

            # Asset statistics table
            asset_stats = []
            for asset in symbols:
                asset_return = optimizer.mean_returns[asset]
                asset_vol = np.sqrt(optimizer.cov_matrix.loc[asset, asset])
                asset_sharpe = (asset_return - risk_free_rate) / asset_vol

                asset_stats.append(
                    {
                        "Asset": asset,
                        "Expected Return (%)": f"{asset_return*100:.2f}",
                        "Volatility (%)": f"{asset_vol*100:.2f}",
                        "Sharpe Ratio": f"{asset_sharpe:.4f}",
                    }
                )

            asset_stats_df = pd.DataFrame(asset_stats)
            st.dataframe(asset_stats_df, use_container_width=True)

            # Portfolio comparison
            st.subheader("⚖️ Portfolio Comparison")

            comparison_data = {
                "Metric": ["Expected Return (%)", "Volatility (%)", "Sharpe Ratio"],
                "Max Sharpe Portfolio": [
                    f"{max_sharpe_portfolio['expected_return']*100:.2f}",
                    f"{max_sharpe_portfolio['volatility']*100:.2f}",
                    f"{max_sharpe_portfolio['sharpe_ratio']:.4f}",
                ],
                "Min Volatility Portfolio": [
                    f"{min_vol_portfolio['expected_return']*100:.2f}",
                    f"{min_vol_portfolio['volatility']*100:.2f}",
                    f"{min_vol_portfolio['sharpe_ratio']:.4f}",
                ],
                "Equal Weight Portfolio": [
                    f"{optimizer.mean_returns.mean()*100:.2f}",
                    f"{np.sqrt(np.mean(np.diag(optimizer.cov_matrix)))*100:.2f}",
                    f"{(optimizer.mean_returns.mean() - risk_free_rate) / np.sqrt(np.mean(np.diag(optimizer.cov_matrix))):.4f}",
                ],
            }

            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)

            # Risk contribution analysis
            st.subheader("⚠️ Risk Contribution Analysis")

            # Calculate marginal risk contributions for max Sharpe portfolio
            weights_max_sharpe = max_sharpe_portfolio["weights"]
            portfolio_variance = np.dot(
                weights_max_sharpe.T, np.dot(optimizer.cov_matrix, weights_max_sharpe)
            )
            marginal_contrib = np.dot(
                optimizer.cov_matrix, weights_max_sharpe
            ) / np.sqrt(portfolio_variance)
            risk_contrib = weights_max_sharpe * marginal_contrib
            risk_contrib_pct = risk_contrib / risk_contrib.sum() * 100

            risk_contrib_df = pd.DataFrame(
                {
                    "Asset": symbols,
                    "Weight (%)": weights_max_sharpe * 100,
                    "Risk Contribution (%)": risk_contrib_pct,
                }
            ).round(2)
            risk_contrib_df = risk_contrib_df[
                risk_contrib_df["Weight (%)"] > 0.1
            ].sort_values("Risk Contribution (%)", ascending=False)

            st.dataframe(risk_contrib_df, use_container_width=True)

            # Risk contribution chart
            fig_risk_contrib = go.Figure()
            fig_risk_contrib.add_trace(
                go.Bar(
                    x=risk_contrib_df["Asset"],
                    y=risk_contrib_df["Risk Contribution (%)"],
                    name="Risk Contribution",
                    marker_color="lightcoral",
                )
            )
            fig_risk_contrib.add_trace(
                go.Bar(
                    x=risk_contrib_df["Asset"],
                    y=risk_contrib_df["Weight (%)"],
                    name="Portfolio Weight",
                    marker_color="lightblue",
                )
            )

            fig_risk_contrib.update_layout(
                title="Risk Contribution vs Portfolio Weight",
                xaxis_title="Assets",
                yaxis_title="Percentage (%)",
                barmode="group",
            )

            st.plotly_chart(fig_risk_contrib, use_container_width=True)

            # Monte Carlo simulation preview
            st.subheader("🎲 Portfolio Performance Simulation")

            # Simple Monte Carlo simulation
            n_simulations = 1000
            time_horizon = 252  # 1 year

            # Calculate portfolio statistics
            portfolio_mean = (returns_data * weights_max_sharpe).sum(axis=1).mean()
            portfolio_std = (returns_data * weights_max_sharpe).sum(axis=1).std()

            # Generate random returns
            random_returns = np.random.normal(
                portfolio_mean, portfolio_std, (n_simulations, time_horizon)
            )

            # Calculate portfolio paths
            portfolio_values = np.zeros((n_simulations, time_horizon + 1))
            portfolio_values[:, 0] = 10000  # Initial investment

            for t in range(1, time_horizon + 1):
                portfolio_values[:, t] = portfolio_values[:, t - 1] * (
                    1 + random_returns[:, t - 1]
                )

            # Plot simulation results
            fig_simulation = go.Figure()

            # Plot sample paths
            sample_paths = np.random.choice(n_simulations, 100, replace=False)
            for i in sample_paths:
                fig_simulation.add_trace(
                    go.Scatter(
                        x=list(range(time_horizon + 1)),
                        y=portfolio_values[i],
                        mode="lines",
                        line=dict(width=1, color="lightblue"),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )

            # Add mean path
            mean_path = np.mean(portfolio_values, axis=0)
            fig_simulation.add_trace(
                go.Scatter(
                    x=list(range(time_horizon + 1)),
                    y=mean_path,
                    mode="lines",
                    name="Mean Path",
                    line=dict(width=3, color="red"),
                )
            )

            # Add confidence bands
            upper_95 = np.percentile(portfolio_values, 97.5, axis=0)
            lower_5 = np.percentile(portfolio_values, 2.5, axis=0)

            fig_simulation.add_trace(
                go.Scatter(
                    x=list(range(time_horizon + 1)),
                    y=upper_95,
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                )
            )

            fig_simulation.add_trace(
                go.Scatter(
                    x=list(range(time_horizon + 1)),
                    y=lower_5,
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(255, 0, 0, 0.1)",
                    name="95% Confidence Band",
                )
            )

            fig_simulation.update_layout(
                title="Portfolio Value Simulation (1 Year)",
                xaxis_title="Trading Days",
                yaxis_title="Portfolio Value ($)",
                hovermode="x unified",
            )

            st.plotly_chart(fig_simulation, use_container_width=True)

            # Simulation statistics
            final_values = portfolio_values[:, -1]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                mean_final = np.mean(final_values)
                st.metric("Mean Final Value", f"${mean_final:,.0f}")

            with col2:
                prob_loss = np.mean(final_values < 10000) * 100
                st.metric("Probability of Loss", f"{prob_loss:.1f}%")

            with col3:
                var_95 = np.percentile((final_values - 10000) / 10000, 5) * 100
                st.metric("VaR (95%)", f"{abs(var_95):.1f}%")

            with col4:
                best_case = np.percentile(final_values, 95)
                st.metric("95th Percentile", f"${best_case:,.0f}")

            # Export functionality
            st.subheader("📄 Export Results")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📋 Generate PDF Report"):
                    with st.spinner("Generating PDF report..."):
                        # Prepare portfolio data for report
                        portfolio_data = {
                            "asset_names": symbols,
                            "returns_data": returns_data,
                            "max_sharpe": max_sharpe_portfolio,
                            "min_volatility": min_vol_portfolio,
                        }

                        pdf_bytes = (
                            report_generator.generate_portfolio_optimization_report(
                                frontier_data,
                                portfolio_data,
                                f"Optimized Portfolio ({len(symbols)} assets)",
                            )
                        )

                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"portfolio_optimization_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                        )

            with col2:
                if st.button("📊 Export Data to CSV"):
                    csv_data = {
                        "returns_data": returns_data,
                        "max_sharpe_weights": pd.DataFrame(
                            {
                                "Asset": symbols,
                                "Weight": max_sharpe_portfolio["weights"],
                            }
                        ),
                        "min_vol_weights": pd.DataFrame(
                            {"Asset": symbols, "Weight": min_vol_portfolio["weights"]}
                        ),
                        "efficient_frontier": pd.DataFrame(
                            {
                                "Return": frontier_data["returns"],
                                "Volatility": frontier_data["volatility"],
                            }
                        ),
                        "correlation_matrix": returns_data.corr(),
                        "asset_statistics": asset_stats_df,
                    }

                    csv_files = report_generator.export_data_to_csv(
                        csv_data, "portfolio_optimization"
                    )

                    for filename, csv_bytes in csv_files.items():
                        st.download_button(
                            label=f"⬇️ Download {filename}",
                            data=csv_bytes,
                            file_name=filename,
                            mime="text/csv",
                        )

    except Exception as e:
        st.error(f"An error occurred during optimization: {str(e)}")
        st.exception(e)

else:
    # Initial instructions
    st.info("""
    ## 🚀 Getting Started with Portfolio Optimization
    
    1. **Select Asset Universe**: Enter stock symbols for optimization (minimum 2 assets)
    2. **Choose Data Period**: Select historical period for return/risk estimation
    3. **Set Risk-Free Rate**: Configure the risk-free rate for Sharpe ratio calculation
    4. **Configure Constraints**: Set minimum and maximum weights per asset
    5. **Run Optimization**: Click "Optimize Portfolio" to find optimal allocations
    
    ### 📊 Optimization Features
    - **Efficient Frontier**: Visualization of optimal risk-return combinations
    - **Maximum Sharpe Ratio**: Portfolio with best risk-adjusted returns
    - **Minimum Volatility**: Lowest risk portfolio for conservative investors
    - **Correlation Analysis**: Asset relationship heatmaps and scatter plots
    - **Risk Contribution**: Analysis of each asset's contribution to portfolio risk
    - **Monte Carlo Simulation**: Forward-looking portfolio performance scenarios
    - **Professional Reports**: PDF reports and CSV data exports
    
    ### 🎯 Modern Portfolio Theory
    This optimizer implements **Modern Portfolio Theory (MPT)** developed by Harry Markowitz:
    
    - **Diversification Benefits**: Reduces portfolio risk through uncorrelated assets
    - **Efficient Frontier**: Set of portfolios offering maximum return for each risk level
    - **Sharpe Ratio Optimization**: Maximizes excess return per unit of risk
    - **Mean-Variance Framework**: Uses historical returns and covariances for optimization
    
    ### 📈 Investment Strategies
    - **Growth-Oriented**: Use Maximum Sharpe Ratio portfolio for higher returns
    - **Conservative**: Use Minimum Volatility portfolio for lower risk
    - **Balanced**: Choose a point on the efficient frontier matching your risk tolerance
    - **Risk Parity**: Consider risk contribution analysis for balanced risk exposure
    """)

    # Display sample efficient frontier
    if st.button("📊 View Sample Efficient Frontier"):
        # Create sample data for demonstration
        sample_returns = np.array([0.08, 0.12, 0.15, 0.10])
        sample_volatilities = np.array([0.15, 0.20, 0.30, 0.18])
        sample_assets = [
            "Conservative Bond",
            "Balanced Fund",
            "Growth Stock",
            "Dividend Stock",
        ]

        fig_sample = go.Figure()

        # Sample efficient frontier curve
        frontier_vol = np.linspace(0.15, 0.25, 50)
        frontier_ret = 0.08 + (frontier_vol - 0.15) * 0.4

        fig_sample.add_trace(
            go.Scatter(
                x=frontier_vol,
                y=frontier_ret,
                mode="lines",
                name="Efficient Frontier",
                line=dict(color="blue", width=3),
            )
        )

        # Sample assets
        fig_sample.add_trace(
            go.Scatter(
                x=sample_volatilities,
                y=sample_returns,
                mode="markers+text",
                text=sample_assets,
                textposition="top center",
                name="Sample Assets",
                marker=dict(size=12, color=["green", "blue", "red", "orange"]),
            )
        )

        # Optimal portfolio
        fig_sample.add_trace(
            go.Scatter(
                x=[0.18],
                y=[0.115],
                mode="markers",
                name="Optimal Portfolio",
                marker=dict(size=15, color="red", symbol="star"),
            )
        )

        fig_sample.update_layout(
            title="Sample Efficient Frontier",
            xaxis_title="Risk (Volatility)",
            yaxis_title="Expected Return",
            hovermode="closest",
            showlegend=True,
        )

        st.plotly_chart(fig_sample, use_container_width=True)

        st.caption(
            "This is a sample efficient frontier showing the concept. Use real data for actual optimization."
        )
