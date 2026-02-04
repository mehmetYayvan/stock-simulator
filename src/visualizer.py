"""Visualization functions for stock data."""

from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf


def plot_stock_performance(
    tickers: list[str],
    start_date: datetime,
    end_date: datetime,
    initial_amount: float = 1000.0,
    save_path: str = None,
):
    """
    Plot the performance of stocks over time.

    Args:
        tickers: List of stock ticker symbols
        start_date: Start date for the chart
        end_date: End date for the chart
        initial_amount: Initial investment amount (for normalization)
        save_path: Optional path to save the chart image
    """
    plt.figure(figsize=(12, 6))

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                print(f"No data for {ticker}")
                continue

            # Normalize to initial investment
            initial_price = hist['Close'].iloc[0]
            normalized = (hist['Close'] / initial_price) * initial_amount

            plt.plot(normalized.index, normalized.values, label=ticker, linewidth=2)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    plt.title(f"Investment Performance: ${initial_amount:,.0f} invested on {start_date.strftime('%Y-%m-%d')}")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)

    # Format x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Chart saved to {save_path}")
    else:
        plt.show()


def plot_portfolio_comparison(
    scenarios: list[dict],
    start_date: datetime,
    end_date: datetime,
    save_path: str = None,
):
    """
    Plot comparison of different portfolio scenarios.

    Args:
        scenarios: List of dicts with 'name' and 'holdings' (list of (ticker, amount))
        start_date: Start date
        end_date: End date
        save_path: Optional path to save
    """
    plt.figure(figsize=(12, 6))

    for scenario in scenarios:
        name = scenario['name']
        holdings = scenario['holdings']

        # Get price data for each holding
        portfolio_value = None

        for ticker, amount in holdings:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)

                if hist.empty:
                    continue

                initial_price = hist['Close'].iloc[0]
                shares = amount / initial_price
                value = hist['Close'] * shares

                if portfolio_value is None:
                    portfolio_value = value
                else:
                    # Align indices
                    portfolio_value = portfolio_value.add(value, fill_value=0)
            except Exception:
                continue

        if portfolio_value is not None:
            plt.plot(portfolio_value.index, portfolio_value.values, label=name, linewidth=2)

    plt.title(f"Scenario Comparison ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Chart saved to {save_path}")
    else:
        plt.show()
