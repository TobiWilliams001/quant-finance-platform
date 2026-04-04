# Quantitative Finance Analytics Platform

**Professional-grade financial analytics platform for institutional risk assessment and derivatives pricing**

A comprehensive Streamlit-based application that implements sophisticated financial models used by investment banks and hedge funds. This platform bridges academic quantitative finance theory with practical institutional applications, featuring real-time market data integration and professional-grade analytics.

![Platform Overview](https://img.shields.io/badge/Python-3.11+-blue.svg) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features & Capabilities

### Risk Analytics
- **Value at Risk (VaR)** calculations at multiple confidence levels (90%, 95%, 99%)
- **Conditional Value at Risk (CVaR)** for tail risk assessment  
- **Maximum Drawdown** analysis with time series visualization
- **Sharpe & Sortino Ratios** for risk-adjusted performance metrics
- **Distribution Analysis** including skewness, kurtosis, and normality tests
- **Benchmark Comparison** with beta, tracking error, and information ratio

### Portfolio Optimization  
- **Modern Portfolio Theory** implementation with efficient frontier
- **Sharpe Ratio Maximization** for optimal risk-adjusted returns
- **Minimum Volatility** portfolios for conservative strategies
- **Correlation Analysis** with interactive correlation heatmaps
- **Risk-Return Visualization** with scatter plots and efficient frontiers

### Options Pricing
- **Black-Scholes-Merton Model** for European options valuation
- **Complete Greeks Calculation**: Delta, Gamma, Theta, Vega, Rho
- **Sensitivity Analysis** for parameter impact assessment
- **Moneyness Classification** (ITM, ATM, OTM)
- **Time Decay Visualization** and volatility impact analysis

### Monte Carlo Simulations
- **Geometric Brownian Motion** for price path simulation
- **Jump Diffusion Models** for extreme event modeling
- **Mean Reversion Processes** for interest rate modeling
- **Portfolio Performance Simulation** with confidence intervals
- **Options Pricing via Monte Carlo** methods

### Pairs Trading
- **Cointegration Testing** using Engle-Granger methodology
- **Hedge Ratio Calculation** via Ordinary Least Squares regression
- **Z-Score Monitoring** for real-time spread analysis
- **Signal Generation** for automated entry/exit points
- **Backtesting Framework** for strategy validation

### Professional Reporting
- **PDF Report Generation** with institutional-grade formatting
- **CSV Data Export** for all analysis results and calculations
- **Excel Integration** via openpyxl for structured exports
- **Interactive Visualizations** using Plotly for charts and graphs

## Technical Architecture

### Frontend Framework
- **Streamlit**: Multi-page application with professional UI/UX
- **Plotly**: Interactive financial charts and visualizations
- **Custom CSS**: Professional styling and branding

### Backend Infrastructure  
- **Python 3.11+**: Core computational engine
- **NumPy & SciPy**: Numerical computing and statistical analysis
- **Pandas**: Data manipulation and time series analysis
- **scikit-learn**: Machine learning for regression analysis
- **yfinance**: Real-time market data integration

### Financial Libraries
- **ReportLab**: Professional PDF generation
- **openpyxl**: Excel file processing
- **statsmodels**: Advanced statistical modeling
- **scipy.stats**: Statistical distributions and tests

## Prerequisites

Before installation, ensure you have the following:

- **Python 3.11 or higher**
- **pip** (Python package installer)
- **Git** (for cloning the repository)
- **8GB+ RAM** recommended for large portfolio analysis
- **Internet connection** for real-time market data

## Installation & Setup

### Option 1: Local Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/quant-finance-platform.git
   cd quant-finance-platform
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create Required Directories**
   ```bash
   mkdir -p .streamlit
   mkdir -p data/exports
   mkdir -p logs
   ```

5. **Configure Streamlit** (Create `.streamlit/config.toml`)
   ```toml
   [server]
   headless = true
   address = "0.0.0.0"
   port = 8501
   
   [theme]
   base = "light"
   primaryColor = "#1f77b4"
   backgroundColor = "#ffffff"
   secondaryBackgroundColor = "#f0f2f6"
   ```

6. **Run the Application**
   ```bash
   streamlit run app.py
   ```

7. **Access the Platform**
   - Open your browser and navigate to: `http://localhost:8501`

### Option 2: Docker Installation

1. **Build Docker Image**
   ```bash
   docker build -t quant-finance-platform .
   ```

2. **Run Container**
   ```bash
   docker run -p 8501:8501 quant-finance-platform
   ```

## 📦 Dependencies

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
yfinance>=0.2.20
scikit-learn>=1.3.0
scipy>=1.11.0
statsmodels>=0.14.0
reportlab>=4.0.0
openpyxl>=3.1.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
```

## Quick Start Guide

### 1. Risk Analytics Module
- Navigate to **Risk Analytics** page
- Enter stock symbols (e.g., AAPL, GOOGL, MSFT)
- Configure analysis period and risk parameters
- Click **"Run Risk Analysis"** or **"Try Sample Analysis"**
- Generate PDF reports and export CSV data

### 2. Portfolio Optimization
- Go to **Portfolio Optimization** page  
- Input portfolio symbols and expected returns
- Set risk tolerance and constraints
- Run optimization to find efficient frontier
- Export optimized portfolio weights

### 3. Options Pricing
- Access **Options Pricing** module
- Enter option parameters (spot price, strike, expiry, etc.)
- Calculate Black-Scholes price and Greeks
- Perform sensitivity analysis
- Generate professional reports

### 4. Monte Carlo Simulation
- Visit **Monte Carlo Simulation** page
- Choose simulation type (GBM, Jump Diffusion, etc.)
- Configure parameters and run simulations
- Analyze confidence intervals and statistics
- Export simulation results

### 5. Pairs Trading Analysis
- Open **Pairs Trading** module
- Select two stocks for pairs analysis
- Run cointegration tests and calculate hedge ratios
- Monitor Z-scores for trading signals
- Backtest trading strategies

## 🔒 Environment Configuration

Create a `.env` file in the project root for sensitive configurations:

```env
# API Keys (Optional - for enhanced data sources)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
QUANDL_API_KEY=your_quandl_key

# Database Configuration (If using PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/quant_finance
DB_HOST=localhost
DB_PORT=5432
DB_NAME=quant_finance
DB_USER=your_username
DB_PASSWORD=your_password

# Application Settings
LOG_LEVEL=INFO
CACHE_TTL=300
MAX_PORTFOLIO_SIZE=50
```

## 🗄️ Database Setup (Optional)

For data persistence and historical analysis storage:

### PostgreSQL Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows: Download from postgresql.org
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE quant_finance;
   CREATE USER quant_user WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE quant_finance TO quant_user;
   ```

3. **Initialize Tables**
   ```bash
   python scripts/init_database.py
   ```

## Data Sources

### Primary Data Provider
- **Yahoo Finance API**: Real-time and historical market data
- **Coverage**: Global stocks, indices, ETFs, bonds, commodities
- **Rate Limits**: Built-in caching with 5-minute TTL
- **Reliability**: Free tier with good data quality

### Alternative Data Sources (Optional)
- **Alpha Vantage**: Premium market data with API key
- **Quandl**: Economic and financial datasets
- **FRED**: Federal Reserve economic data

## Use Cases

### For Students & Educators
- **Learning Tool**: Understand quantitative finance concepts
- **Academic Research**: Implement and test financial models
- **Course Projects**: Analyze real market data with professional tools

### For Investment Professionals  
- **Risk Management**: Calculate portfolio VaR and stress testing
- **Options Trading**: Price derivatives and analyze Greeks
- **Portfolio Management**: Optimize asset allocation strategies

### For Quantitative Analysts
- **Model Validation**: Test and compare financial models
- **Backtesting**: Historical performance analysis
- **Research & Development**: Prototype new trading strategies

## 🤝 Contributing

We welcome contributions from the quantitative finance community!

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 Python style guidelines
- Add unit tests for new features
- Update documentation for API changes
- Include docstrings for all functions and classes

## 🔍 Testing

Run the test suite to ensure everything works correctly:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=utils --cov=pages

# Run specific test module
pytest tests/test_risk_analytics.py
```

## 📝 Documentation

### Code Documentation
- All functions include comprehensive docstrings
- Type hints are used throughout the codebase
- Inline comments explain complex financial calculations

### API Reference
- Detailed module documentation in `docs/api/`
- Mathematical formulas and derivations
- Example usage and code samples

## Important Notes

### Disclaimer
This platform is for educational and research purposes. All financial calculations are provided "as-is" without warranty. Users should not rely solely on this software for investment decisions. Always consult with qualified financial professionals before making investment choices.

### Data Accuracy
- Market data is sourced from third-party providers
- Real-time data may have slight delays
- Historical data accuracy depends on data source quality
- Users should validate results with multiple sources

### Performance Considerations
- Large portfolios (>50 assets) may require significant processing time
- Monte Carlo simulations with high iteration counts can be memory-intensive
- Consider using smaller datasets for initial testing

## 📞 Support & Community

### Getting Help
- **Documentation**: Comprehensive guides and API reference
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Community Q&A and feature discussions

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments
- Built with [Streamlit](https://streamlit.io/) for the web framework
- Market data provided by [Yahoo Finance](https://finance.yahoo.com/)
- PDF generation powered by [ReportLab](https://www.reportlab.com/)
- Financial calculations based on established academic research

## Roadmap

### Version 2.0 (Upcoming)
- **Real-time Portfolio Tracking**: Live P&L monitoring
- **Advanced Options Strategies**: Complex multi-leg strategies
- **Machine Learning Models**: AI-powered risk prediction
- **API Integration**: REST API for programmatic access

### Future Enhancements
- **Cryptocurrency Analytics**: Digital asset risk assessment
- **ESG Integration**: Environmental, Social, Governance metrics
- **Alternative Data Sources**: Satellite data, news sentiment
- **Advanced Backtesting**: Walk-forward analysis and optimization

---

**Built with ❤️ for the quantitative finance community**

*Empowering the next generation of quantitative analysts with institutional-grade tools*