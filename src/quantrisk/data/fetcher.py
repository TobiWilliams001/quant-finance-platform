import warnings
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")


class DataFetcher:
    """Handles all market data fetching operations"""

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    @st.cache_data(ttl=300)
    def fetch_stock_data(
        _self, symbols: str or List[str], period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch stock data from Yahoo Finance

        Args:
            symbols: Stock symbol(s) to fetch
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            if isinstance(symbols, str):
                ticker = yf.Ticker(symbols)
                data = ticker.history(period=period, interval=interval)
                if data.empty:
                    raise ValueError(f"No data found for symbol {symbols}")
                return data
            else:
                # Multiple symbols
                data = yf.download(
                    symbols, period=period, interval=interval, group_by="ticker"
                )
                if data.empty:
                    raise ValueError(f"No data found for symbols {symbols}")
                return data
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)
    def fetch_multiple_stocks(
        _self, symbols: List[str], period: str = "1y"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks

        Args:
            symbols: List of stock symbols
            period: Time period

        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        stock_data = {}

        for symbol in symbols:
            try:
                data = _self.fetch_stock_data(symbol, period)
                if not data.empty:
                    stock_data[symbol] = data
            except Exception as e:
                st.warning(f"Could not fetch data for {symbol}: {str(e)}")
                continue

        return stock_data

    @st.cache_data(ttl=300)
    def get_returns_matrix(
        _self, symbols: List[str], period: str = "1y"
    ) -> pd.DataFrame:
        """
        Get returns matrix for multiple stocks

        Args:
            symbols: List of stock symbols
            period: Time period

        Returns:
            DataFrame with daily returns for each stock
        """
        try:
            # Fetch data for all symbols at once
            data = yf.download(symbols, period=period, group_by="ticker")

            if data.empty:
                return pd.DataFrame()

            returns_data = {}

            if len(symbols) == 1:
                # Single stock
                close_prices = data["Close"]
                returns = close_prices.pct_change().dropna()
                returns_data[symbols[0]] = returns
            else:
                # Multiple stocks
                for symbol in symbols:
                    try:
                        if symbol in data.columns.get_level_values(0):
                            close_prices = data[symbol]["Close"]
                            returns = close_prices.pct_change().dropna()
                            returns_data[symbol] = returns
                    except Exception as e:
                        st.warning(
                            f"Could not calculate returns for {symbol}: {str(e)}"
                        )
                        continue

            returns_df = pd.DataFrame(returns_data)
            return returns_df.dropna()

        except Exception as e:
            st.error(f"Error calculating returns matrix: {str(e)}")
            return pd.DataFrame()

    @st.cache_data(ttl=300)
    def get_stock_info(_self, symbol: str) -> Dict:
        """
        Get stock information and metrics

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with stock information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract relevant information
            stock_info = {
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "beta": info.get("beta", 0),
                "price": info.get("currentPrice", 0),
            }

            return stock_info

        except Exception as e:
            st.error(f"Error fetching stock info for {symbol}: {str(e)}")
            return {}

    def validate_symbols(self, symbols: List[str]) -> List[str]:
        """
        Validate that symbols exist and have data

        Args:
            symbols: List of stock symbols to validate

        Returns:
            List of valid symbols
        """
        valid_symbols = []

        for symbol in symbols:
            try:
                data = self.fetch_stock_data(symbol, period="5d")
                if not data.empty and len(data) > 0:
                    valid_symbols.append(symbol)
                else:
                    st.warning(f"Symbol {symbol} has no data available")
            except Exception as e:
                st.warning(f"Symbol {symbol} is invalid: {str(e)}")

        return valid_symbols

    @st.cache_data(ttl=1800)  # 30 minutes cache for risk-free rate
    def get_risk_free_rate(_self) -> float:
        """
        Get current risk-free rate (10-year Treasury yield)

        Returns:
            Risk-free rate as decimal
        """
        try:
            treasury = yf.Ticker("^TNX")
            data = treasury.history(period="5d")
            if not data.empty:
                rate = data["Close"].iloc[-1] / 100  # Convert percentage to decimal
                return rate
            else:
                return 0.02  # Default 2% if data unavailable
        except Exception:
            return 0.02  # Default 2% if error
