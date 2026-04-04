"""
QuantRisk - Professional Quantitative Finance Analytics Platform
"""

__version__ = "0.1.0"
__author__ = "Tobi Williams"

# Core imports for easy access
from .analytics import monte_carlo, options, pairs_trading, portfolio, risk
from .data import database, fetcher
from .utils import reports

__all__ = [
    "risk",
    "portfolio",
    "options",
    "monte_carlo",
    "pairs_trading",
    "fetcher",
    "database",
    "reports",
]
