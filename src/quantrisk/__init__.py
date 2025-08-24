"""
QuantRisk - Professional Quantitative Finance Analytics Platform
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# Core imports for easy access
from .analytics import risk, portfolio, options, monte_carlo, pairs_trading
from .data import fetcher, database
from .utils import reports

__all__ = [
    "risk",
    "portfolio", 
    "options",
    "monte_carlo",
    "pairs_trading",
    "fetcher",
    "database",
    "reports"
]
