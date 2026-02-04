"""Command-line interface for stock simulator."""

import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
import click

from .fetcher import get_stock_price, get_current_price, StockDataError
from .simulator import (
    simulate_investment, simulate_portfolio, rank_investments,
    RankingResult, ScenarioResult, ComparisonResult, BenchmarkResult, DCAResult
)
from .visualizer import plot_stock_performance, plot_portfolio_comparison


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
@click.option('--benchmark', '-b', is_flag=True, help='Compare against S&P 500 (SPY)')
def simulate(ticker: str, date: str, amount: float, sell_date: str, benchmark: bool):
    """
    Simulate a stock investment.

    Example: stock-sim simulate AAPL --date 2020-01-01 --amount 1000
    Example with benchmark: stock-sim simulate AAPL --date 2020-01-01 --amount 1000 --benchmark
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

    if benchmark:
        # Fetch SPY data for comparison
        try:
            spy_buy_price, spy_name = get_stock_price('SPY', buy_date)
            if sell_date:
                spy_sell_price, _ = get_stock_price('SPY', sell_dt)
            else:
                spy_sell_price = get_current_price('SPY')

            spy_result = simulate_investment(
                ticker='SPY',
                company_name=spy_name,
                buy_date=buy_date,
                buy_price=spy_buy_price,
                sell_date=sell_dt,
                sell_price=spy_sell_price,
                investment_amount=amount,
            )

            benchmark_result = BenchmarkResult(investment=result, benchmark=spy_result)
            click.echo("\n" + str(benchmark_result))
        except StockDataError as e:
            click.echo(f"Warning: Could not fetch benchmark data: {e}", err=True)
            click.echo("\n" + "=" * 45)
            click.echo(str(result))
            click.echo("=" * 45)
    else:
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


@cli.command()
@click.argument('scenarios', nargs=-1, required=True)
@click.option('--date', '-d', required=True, help='Buy date (YYYY-MM-DD)')
@click.option('--sell-date', '-s', default=None, help='Sell date (YYYY-MM-DD). Defaults to today.')
def compare(scenarios: tuple, date: str, sell_date: str):
    """
    Compare different investment scenarios.

    SCENARIOS format: "TICKER:AMOUNT,TICKER:AMOUNT" (quoted, comma-separated)

    Example: stock-sim compare "AAPL:1000,TSLA:500" "MSFT:800,GOOGL:700" --date 2020-01-01
    """
    if len(scenarios) < 2:
        click.echo("Error: Need at least 2 scenarios to compare.", err=True)
        sys.exit(1)

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

    click.echo(f"Comparing {len(scenarios)} scenarios...")

    scenario_results = []
    for i, scenario_str in enumerate(scenarios, 1):
        # Parse holdings from "AAPL:1000,TSLA:500" format
        holdings_strs = scenario_str.split(',')
        holdings = []

        for h in holdings_strs:
            h = h.strip()
            if ':' not in h:
                click.echo(f"Error: Invalid format '{h}' in scenario {i}. Use TICKER:AMOUNT.", err=True)
                sys.exit(1)
            parts = h.split(':')
            if len(parts) != 2:
                click.echo(f"Error: Invalid format '{h}' in scenario {i}. Use TICKER:AMOUNT.", err=True)
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
                holdings.append(result)
            except StockDataError as e:
                click.echo(f"Error fetching {ticker}: {e}", err=True)
                sys.exit(1)

        total_invested = sum(h.investment_amount for h in holdings)
        total_value = sum(h.final_value for h in holdings)
        percent_return = ((total_value - total_invested) / total_invested) * 100 if total_invested > 0 else 0

        scenario_results.append(ScenarioResult(
            name=f"Scenario {i}",
            holdings=holdings,
            total_invested=total_invested,
            total_value=total_value,
            percent_return=percent_return,
        ))

    comparison = ComparisonResult(
        scenarios=scenario_results,
        buy_date=buy_date,
        sell_date=sell_dt,
    )
    click.echo("\n" + str(comparison))


@cli.command()
@click.argument('tickers', nargs=-1, required=True)
@click.option('--date', '-d', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', default=None, help='End date (YYYY-MM-DD). Defaults to today.')
@click.option('--amount', '-a', default=1000.0, type=float, help='Investment amount (default: 1000)')
@click.option('--save', '-o', default=None, help='Save chart to file (e.g., chart.png)')
def chart(tickers: tuple, date: str, end_date: str, amount: float, save: str):
    """
    Visualize stock performance over time.

    Example: stock-sim chart AAPL TSLA MSFT --date 2020-01-01
    """
    try:
        start_dt = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        click.echo(f"Error: Invalid date format '{date}'. Use YYYY-MM-DD.", err=True)
        sys.exit(1)

    if start_dt > datetime.now():
        click.echo("Error: Start date cannot be in the future.", err=True)
        sys.exit(1)

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            click.echo(f"Error: Invalid end date format '{end_date}'. Use YYYY-MM-DD.", err=True)
            sys.exit(1)
    else:
        end_dt = datetime.now()

    tickers = [t.upper() for t in tickers]
    click.echo(f"Generating chart for {len(tickers)} stocks...")

    plot_stock_performance(
        tickers=tickers,
        start_date=start_dt,
        end_date=end_dt,
        initial_amount=amount,
        save_path=save,
    )


@cli.command()
@click.argument('ticker')
@click.option('--date', '-d', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', default=None, help='End date (YYYY-MM-DD). Defaults to today.')
@click.option('--amount', '-a', default=500.0, type=float, help='Amount per month (default: 500)')
def dca(ticker: str, date: str, end_date: str, amount: float):
    """
    Simulate dollar-cost averaging (monthly investments).

    Example: stock-sim dca AAPL --date 2020-01-01 --amount 500
    """
    ticker = ticker.upper()

    try:
        start_dt = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        click.echo(f"Error: Invalid date format '{date}'. Use YYYY-MM-DD.", err=True)
        sys.exit(1)

    if start_dt > datetime.now():
        click.echo("Error: Start date cannot be in the future.", err=True)
        sys.exit(1)

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            click.echo(f"Error: Invalid end date format '{end_date}'. Use YYYY-MM-DD.", err=True)
            sys.exit(1)
    else:
        end_dt = datetime.now()

    if amount <= 0:
        click.echo("Error: Amount must be positive.", err=True)
        sys.exit(1)

    click.echo(f"Simulating DCA for {ticker}...")

    # Get company name
    try:
        _, company_name = get_stock_price(ticker, start_dt)
    except StockDataError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Calculate purchases for each month
    total_shares = 0.0
    total_invested = 0.0
    num_purchases = 0
    current_date = start_dt

    while current_date <= end_dt:
        try:
            price, _ = get_stock_price(ticker, current_date)
            shares = amount / price
            total_shares += shares
            total_invested += amount
            num_purchases += 1
        except StockDataError:
            pass  # Skip months with no data

        current_date = current_date + relativedelta(months=1)

    if num_purchases == 0:
        click.echo("Error: No valid purchase dates found.", err=True)
        sys.exit(1)

    # Get current price for final value
    try:
        current_price = get_current_price(ticker)
    except StockDataError as e:
        click.echo(f"Error getting current price: {e}", err=True)
        sys.exit(1)

    final_value = total_shares * current_price
    profit = final_value - total_invested
    percent_return = (profit / total_invested) * 100 if total_invested > 0 else 0
    avg_cost = total_invested / total_shares if total_shares > 0 else 0

    result = DCAResult(
        ticker=ticker,
        company_name=company_name,
        start_date=start_dt,
        end_date=end_dt,
        amount_per_period=amount,
        num_purchases=num_purchases,
        total_invested=total_invested,
        total_shares=total_shares,
        final_value=final_value,
        profit=profit,
        percent_return=percent_return,
        avg_cost_per_share=avg_cost,
        current_price=current_price,
    )

    click.echo("\n" + str(result))


if __name__ == '__main__':
    cli()
