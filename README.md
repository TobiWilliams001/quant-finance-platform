# Quant Finance Analytics

A Streamlit app for exploring core quantitative finance models on real market data: risk metrics, portfolio optimisation, options pricing, Monte Carlo simulation and pairs trading.

I built it to understand these models by implementing them end to end, from fetching prices to the maths to the charts, rather than calling them from a black-box library. It is a learning and research tool, not a trading system.

## What it does

| Page | What you can do |
|---|---|
| **Risk Analytics** | Historical VaR and CVaR, maximum drawdown, Sharpe and Sortino ratios, beta, tracking error and information ratio against a benchmark |
| **Portfolio Optimisation** | Mean-variance optimisation: maximum-Sharpe and minimum-variance portfolios, the efficient frontier, correlation heatmaps |
| **Options Pricing** | Black-Scholes-Merton prices for European options, the Greeks, implied volatility, payoff and time-decay charts |
| **Monte Carlo Simulation** | Price paths under geometric Brownian motion, jump diffusion and mean reversion; Monte Carlo VaR and option pricing; convergence analysis |
| **Pairs Trading** | Engle-Granger cointegration test, hedge ratio by OLS, z-score signals and a simple backtest |

Results can be exported to CSV, Excel and PDF.

## How it's built

- **Python 3.11+**, with the models in a small package (`src/quantrisk`): `analytics/` for the maths, `data/` for fetching and optional storage, `utils/` for reports
- **NumPy, pandas, SciPy, statsmodels, scikit-learn** for the numerics and statistics
- **Streamlit** multi-page UI with **Plotly** charts
- **yfinance** for market data
- Optional **PostgreSQL** storage via SQLAlchemy (off by default)

## Run it

```bash
git clone https://github.com/TobiWilliams001/quant-finance-platform.git
cd quant-finance-platform
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501.

Database storage is optional. To enable it, copy `config/secrets.example.env` to `.env`, fill in your PostgreSQL details, set `ENABLE_DATABASE=true`, and run `python scripts/init_database.py`.

## Limitations (read before trusting any number)

- **Data:** yfinance data is free and convenient but can be delayed, adjusted or occasionally wrong. It is not a professional data feed.
- **Model assumptions:** Black-Scholes assumes constant volatility and log-normal prices, and the geometric Brownian motion simulations assume normally distributed returns. Real markets have fat tails and changing volatility, which these models understate.
- **Pairs trading backtest:** positions are lagged by one period to avoid look-ahead on signals, but the backtest has **no transaction costs, slippage or financing**, and the pair is tested for cointegration on the same data it is backtested on. Real results would be worse. It shows how the method works, not that it makes money.
- **Optimisation:** mean-variance results are very sensitive to estimated returns and covariances, so small input changes can produce very different portfolios.

## What I learned

Implementing the models myself made their assumptions concrete: where each one breaks, how sensitive the outputs are to inputs, and why an honest backtest needs costs and out-of-sample testing before any result means anything.

## Next

- Add transaction costs and walk-forward (out-of-sample) testing to the pairs backtest
- Add tests for the analytics module against known reference values
- Volatility models that change over time (e.g. GARCH)
