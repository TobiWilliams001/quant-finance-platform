# Quantitative Finance Analytics Platform

## Overview

This is a comprehensive quantitative finance analytics platform built with Streamlit that implements institutional-grade financial models used by investment banks and hedge funds. The application provides professional risk assessment, portfolio optimization, options pricing, Monte Carlo simulations, and pairs trading analysis. It serves as both an educational tool for understanding financial mathematics and a practical platform for conducting sophisticated financial analysis using real market data.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface with multi-page application structure
- **Styling**: Custom CSS for professional appearance with metric cards and consistent branding
- **Visualization**: Plotly for interactive charts and financial plots
- **Layout**: Wide layout with expandable sidebar for parameter configuration
- **Navigation**: Page-based routing with dedicated modules for each analytics function

### Backend Architecture
- **Core Classes**: Modular utility classes for specific financial calculations
  - `DataFetcher`: Market data retrieval and caching
  - `RiskAnalytics`: VaR, CVaR, and risk metric calculations
  - `PortfolioOptimizer`: Modern Portfolio Theory implementation
  - `BlackScholesModel`: Options pricing and Greeks calculations
  - `MonteCarloSimulation`: Probabilistic modeling and simulations
  - `PairsTrading`: Statistical arbitrage and cointegration analysis
  - `ReportGenerator`: PDF and export functionality

### Data Processing
- **Caching Strategy**: Streamlit's `@st.cache_data` decorator with 5-minute TTL for market data
- **Mathematical Libraries**: NumPy and SciPy for numerical computations
- **Statistical Analysis**: Pandas for data manipulation and time series analysis
- **Financial Calculations**: Custom implementations of Black-Scholes, Monte Carlo, and risk models

### Analytics Modules
- **Risk Analytics**: VaR/CVaR calculations, Sharpe ratios, maximum drawdown analysis
- **Portfolio Optimization**: Efficient frontier, mean-variance optimization, correlation analysis
- **Options Pricing**: Black-Scholes model with full Greeks calculation and sensitivity analysis
- **Monte Carlo**: Multiple simulation types including GBM, jump diffusion, and mean reversion
- **Pairs Trading**: Cointegration testing, hedge ratio calculation, and signal generation

### Report Generation
- **Export Formats**: PDF reports using ReportLab, Excel workbooks, CSV data exports
- **Visualization Export**: Plotly figure conversion to images for PDF inclusion
- **Professional Formatting**: Structured reports with charts, tables, and analysis summaries

## External Dependencies

### Market Data Provider
- **Yahoo Finance API**: Primary data source via `yfinance` library for real-time and historical market data
- **Data Coverage**: Stock prices, options data, financial metrics across global markets
- **Rate Limiting**: Built-in caching to respect API limits and improve performance

### Python Libraries
- **Core Framework**: Streamlit for web application framework
- **Data Processing**: Pandas, NumPy for data manipulation and numerical computing
- **Visualization**: Plotly for interactive financial charts and graphs
- **Statistical Analysis**: SciPy, statsmodels for statistical tests and financial calculations
- **Machine Learning**: Scikit-learn for regression analysis in pairs trading
- **Report Generation**: ReportLab for PDF creation, openpyxl for Excel exports

### Financial Models
- **Risk Management**: Historical simulation VaR, parametric CVaR calculations
- **Portfolio Theory**: Modern Portfolio Theory with efficient frontier optimization
- **Derivatives Pricing**: Black-Scholes-Merton model for European options
- **Time Series Analysis**: Cointegration testing using Engle-Granger methodology
- **Simulation Methods**: Geometric Brownian Motion, jump diffusion, mean reversion models

### Database Considerations
- **Current State**: File-based data handling with session state management
- **Scalability**: Architecture supports PostgreSQL integration for persistent storage
- **Data Persistence**: Ready for database integration to store analysis history and user portfolios