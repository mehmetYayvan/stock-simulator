"""Command-line interface for stock simulator."""

import sys
from datetime import datetime
import click

from .fetcher import get_stock_price, get_current_price, StockDataError
from .simulator import simulate_investment, simulate_portfolio, rank_investments, RankingResult


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Stock Investment Simulator - See what your investments could have been worth."""
    pass


@cli.command()
@click.argument('ticker')
@click.option('--date', '-d', required=True, help='Buy date (YYYY-MM-DD)')
@click.option('--amount', '-a', required=True, type=float, help='Investment amount in dollars')
@click.option('--sell-date', '-s', default=None, help='Sell date (YYYY-MM-DD). Defaults to today.')
def simulate(ticker: str, date: str, amount: float, sell_date: str):
    """
    Simulate a stock investment.

    Example: stock-sim simulate AAPL --date 2020-01-01 --amount 1000
    """
    ticker = ticker.upper()

    # Parse buy date
    try:
        buy_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        click.echo(f"Error: Invalid date format '{date}'. Use YYYY-MM-DD.", err=True)
        sys.exit(1)

    # Validate buy date
    if buy_date > datetime.now():
        click.echo("Error: Buy date cannot be in the future.", err=True)
        sys.exit(1)

    # Parse sell date
    if sell_date:
        try:
            sell_dt = datetime.strptime(sell_date, '%Y-%m-%d')
        except ValueError:
            click.echo(f"Error: Invalid sell date format '{sell_date}'. Use YYYY-MM-DD.", err=True)
            sys.exit(1)
        if sell_dt < buy_date:
            click.echo("Error: Sell date cannot be before buy date.", err=True)
            sys.exit(1)
    else:
        sell_dt = datetime.now()

    # Validate amount
    if amount <= 0:
        click.echo("Error: Investment amount must be positive.", err=True)
        sys.exit(1)

    click.echo(f"Fetching data for {ticker}...")

    try:
        # Get buy price
        buy_price, company_name = get_stock_price(ticker, buy_date)

        # Get sell price
        if sell_date:
            sell_price, _ = get_stock_price(ticker, sell_dt)
        else:
            sell_price = get_current_price(ticker)

    except StockDataError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Run simulation
    result = simulate_investment(
        ticker=ticker,
        company_name=company_name,
        buy_date=buy_date,
        buy_price=buy_price,
        sell_date=sell_dt,
        sell_price=sell_price,
        investment_amount=amount,
    )

    click.echo("\n" + "=" * 45)
    click.echo(str(result))
    click.echo("=" * 45)


@cli.command()
@click.argument('ticker')
def price(ticker: str):
    """
    Get the current price for a stock.

    Example: stock-sim price AAPL
    """
    ticker = ticker.upper()

    try:
        current = get_current_price(ticker)
        click.echo(f"{ticker}: ${current:,.2f}")
    except StockDataError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('holdings', nargs=-1, required=True)
@click.option('--date', '-d', required=True, help='Buy date (YYYY-MM-DD)')
@click.option('--sell-date', '-s', default=None, help='Sell date (YYYY-MM-DD). Defaults to today.')
def portfolio(holdings: tuple, date: str, sell_date: str):
    """
    Simulate a portfolio of stocks.

    HOLDINGS format: TICKER:AMOUNT (e.g., AAPL:1000 TSLA:500 MSFT:500)

    Example: stock-sim portfolio AAPL:1000 TSLA:500 --date 2020-01-01
    """
    # Parse buy date
    try:
        buy_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        click.echo(f"Error: Invalid date format '{date}'. Use YYYY-MM-DD.", err=True)
        sys.exit(1)

    if buy_date > datetime.now():
        click.echo("Error: Buy date cannot be in the future.", err=True)
        sys.exit(1)

    # Parse sell date
    if sell_date:
        try:
            sell_dt = datetime.strptime(sell_date, '%Y-%m-%d')
        except ValueError:
            click.echo(f"Error: Invalid sell date format '{sell_date}'. Use YYYY-MM-DD.", err=True)
            sys.exit(1)
        if sell_dt < buy_date:
            click.echo("Error: Sell date cannot be before buy date.", err=True)
            sys.exit(1)
    else:
        sell_dt = datetime.now()

    # Parse holdings
    parsed = []
    for h in holdings:
        if ':' not in h:
            click.echo(f"Error: Invalid holding format '{h}'. Use TICKER:AMOUNT.", err=True)
            sys.exit(1)
        parts = h.split(':')
        if len(parts) != 2:
            click.echo(f"Error: Invalid holding format '{h}'. Use TICKER:AMOUNT.", err=True)
            sys.exit(1)
        ticker = parts[0].upper()
        try:
            amount = float(parts[1])
        except ValueError:
            click.echo(f"Error: Invalid amount in '{h}'.", err=True)
            sys.exit(1)
        if amount <= 0:
            click.echo(f"Error: Amount must be positive in '{h}'.", err=True)
            sys.exit(1)
        parsed.append((ticker, amount))

    click.echo(f"Fetching data for {len(parsed)} stocks...")

    results = []
    for ticker, amount in parsed:
        try:
            buy_price, company_name = get_stock_price(ticker, buy_date)
            if sell_date:
                sell_price, _ = get_stock_price(ticker, sell_dt)
            else:
                sell_price = get_current_price(ticker)

            result = simulate_investment(
                ticker=ticker,
                company_name=company_name,
                buy_date=buy_date,
                buy_price=buy_price,
                sell_date=sell_dt,
                sell_price=sell_price,
                investment_amount=amount,
            )
            results.append(result)
        except StockDataError as e:
            click.echo(f"Error fetching {ticker}: {e}", err=True)
            sys.exit(1)

    portfolio_result = simulate_portfolio(results, buy_date, sell_dt)
    click.echo("\n" + str(portfolio_result))


@cli.command()
@click.argument('tickers', nargs=-1, required=True)
@click.option('--date', '-d', required=True, help='Buy date (YYYY-MM-DD)')
@click.option('--sell-date', '-s', default=None, help='Sell date (YYYY-MM-DD). Defaults to today.')
@click.option('--amount', '-a', default=1000.0, type=float, help='Investment amount (default: 1000)')
@click.option('--top', '-t', default=10, type=int, help='Show top N results (default: 10)')
def best(tickers: tuple, date: str, sell_date: str, amount: float, top: int):
    """
    Find best performing stocks for a time period.

    Example: stock-sim best AAPL TSLA MSFT GOOGL NVDA --date 2020-01-01
    """
    # Parse buy date
    try:
        buy_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        click.echo(f"Error: Invalid date format '{date}'. Use YYYY-MM-DD.", err=True)
        sys.exit(1)

    if buy_date > datetime.now():
        click.echo("Error: Buy date cannot be in the future.", err=True)
        sys.exit(1)

    # Parse sell date
    if sell_date:
        try:
            sell_dt = datetime.strptime(sell_date, '%Y-%m-%d')
        except ValueError:
            click.echo(f"Error: Invalid sell date format '{sell_date}'. Use YYYY-MM-DD.", err=True)
            sys.exit(1)
        if sell_dt < buy_date:
            click.echo("Error: Sell date cannot be before buy date.", err=True)
            sys.exit(1)
    else:
        sell_dt = datetime.now()

    tickers = [t.upper() for t in tickers]
    click.echo(f"Analyzing {len(tickers)} stocks...")

    results = []
    failed = []
    for ticker in tickers:
        try:
            buy_price, company_name = get_stock_price(ticker, buy_date)
            if sell_date:
                sell_price, _ = get_stock_price(ticker, sell_dt)
            else:
                sell_price = get_current_price(ticker)

            result = simulate_investment(
                ticker=ticker,
                company_name=company_name,
                buy_date=buy_date,
                buy_price=buy_price,
                sell_date=sell_dt,
                sell_price=sell_price,
                investment_amount=amount,
            )
            results.append(result)
        except StockDataError:
            failed.append(ticker)

    if failed:
        click.echo(f"Skipped (no data): {', '.join(failed)}")

    if not results:
        click.echo("Error: No valid stocks found.", err=True)
        sys.exit(1)

    ranked = rank_investments(results)[:top]
    ranking_result = RankingResult(
        rankings=ranked,
        buy_date=buy_date,
        sell_date=sell_dt,
        amount=amount,
    )
    click.echo("\n" + str(ranking_result))


if __name__ == '__main__':
    cli()
