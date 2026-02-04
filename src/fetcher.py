"""Fetch historical stock data from Yahoo Finance."""

from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf


class StockDataError(Exception):
    """Raised when stock data cannot be fetched."""
    pass


def get_stock_price(ticker: str, date: datetime) -> tuple[float, str]:
    """
    Get the closing price for a stock on a given date.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        date: Date to get price for

    Returns:
        Tuple of (price, company_name)

    Raises:
        StockDataError: If price cannot be fetched
    """
    stock = yf.Ticker(ticker)

    # Get company name
    try:
        info = stock.info
        company_name = info.get('shortName') or info.get('longName') or ticker
    except Exception:
        company_name = ticker

    # Fetch historical data (get a few days around target date for weekend handling)
    start_date = date - timedelta(days=7)
    end_date = date + timedelta(days=1)

    try:
        hist = stock.history(start=start_date, end=end_date)
    except Exception as e:
        raise StockDataError(f"Failed to fetch data for {ticker}: {e}")

    if hist.empty:
        raise StockDataError(f"No data found for {ticker}. Check if the ticker is valid.")

    # Find the closest date on or before the target date
    hist.index = hist.index.tz_localize(None)  # Remove timezone for comparison
    available_dates = hist.index[hist.index <= date]

    if available_dates.empty:
        raise StockDataError(f"No trading data available for {ticker} on or before {date.strftime('%Y-%m-%d')}")

    closest_date = available_dates[-1]
    price = hist.loc[closest_date, 'Close']

    return float(price), company_name


def get_current_price(ticker: str) -> float:
    """
    Get the current/latest price for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Current stock price

    Raises:
        StockDataError: If price cannot be fetched
    """
    stock = yf.Ticker(ticker)

    try:
        hist = stock.history(period='5d')
    except Exception as e:
        raise StockDataError(f"Failed to fetch current price for {ticker}: {e}")

    if hist.empty:
        raise StockDataError(f"No current data found for {ticker}")

    return float(hist['Close'].iloc[-1])


def validate_ticker(ticker: str) -> bool:
    """Check if a ticker symbol is valid."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d')
        return not hist.empty
    except Exception:
        return False
