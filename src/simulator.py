"""Investment simulation calculations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class InvestmentResult:
    """Results of an investment simulation."""
    ticker: str
    company_name: str
    buy_date: datetime
    buy_price: float
    sell_date: datetime
    sell_price: float
    investment_amount: float
    shares: float
    final_value: float
    profit: float
    percent_return: float
    annualized_return: Optional[float]

    def __str__(self) -> str:
        """Format results for display."""
        lines = [
            f"Stock: {self.ticker} ({self.company_name})",
            f"Buy Date: {self.buy_date.strftime('%Y-%m-%d')} @ ${self.buy_price:,.2f}",
            f"Sell Date: {self.sell_date.strftime('%Y-%m-%d')} @ ${self.sell_price:,.2f}",
            f"Shares: {self.shares:,.4f}",
            "",
            f"Investment: ${self.investment_amount:,.2f} -> ${self.final_value:,.2f}",
        ]

        # Format return with color indicator
        sign = "+" if self.profit >= 0 else ""
        lines.append(f"Return: {sign}${self.profit:,.2f} ({sign}{self.percent_return:.1f}%)")

        if self.annualized_return is not None:
            sign = "+" if self.annualized_return >= 0 else ""
            lines.append(f"Annualized: {sign}{self.annualized_return:.1f}%")

        return "\n".join(lines)


def simulate_investment(
    ticker: str,
    company_name: str,
    buy_date: datetime,
    buy_price: float,
    sell_date: datetime,
    sell_price: float,
    investment_amount: float,
) -> InvestmentResult:
    """
    Simulate an investment and calculate returns.

    Args:
        ticker: Stock ticker symbol
        company_name: Company name
        buy_date: Date of purchase
        buy_price: Price per share at purchase
        sell_date: Date of sale (or current date)
        sell_price: Price per share at sale
        investment_amount: Amount invested in dollars

    Returns:
        InvestmentResult with calculated metrics
    """
    # Calculate shares bought
    shares = investment_amount / buy_price

    # Calculate final value
    final_value = shares * sell_price

    # Calculate profit and returns
    profit = final_value - investment_amount
    percent_return = (profit / investment_amount) * 100

    # Calculate annualized return if more than 1 day
    days_held = (sell_date - buy_date).days
    if days_held > 0:
        years_held = days_held / 365.25
        if years_held >= 0.01:  # At least ~4 days
            total_return = final_value / investment_amount
            annualized_return = (pow(total_return, 1 / years_held) - 1) * 100
        else:
            annualized_return = None
    else:
        annualized_return = None

    return InvestmentResult(
        ticker=ticker,
        company_name=company_name,
        buy_date=buy_date,
        buy_price=buy_price,
        sell_date=sell_date,
        sell_price=sell_price,
        investment_amount=investment_amount,
        shares=shares,
        final_value=final_value,
        profit=profit,
        percent_return=percent_return,
        annualized_return=annualized_return,
    )


@dataclass
class PortfolioResult:
    """Results of a portfolio simulation."""
    holdings: list[InvestmentResult] = field(default_factory=list)
    buy_date: datetime = None
    sell_date: datetime = None
    total_invested: float = 0.0
    total_value: float = 0.0
    total_profit: float = 0.0
    percent_return: float = 0.0
    annualized_return: Optional[float] = None

    def __str__(self) -> str:
        lines = ["PORTFOLIO SUMMARY", "=" * 45]

        for h in self.holdings:
            sign = "+" if h.profit >= 0 else ""
            lines.append(f"{h.ticker}: ${h.investment_amount:,.0f} -> ${h.final_value:,.0f} ({sign}{h.percent_return:.1f}%)")

        lines.append("=" * 45)
        lines.append(f"Period: {self.buy_date.strftime('%Y-%m-%d')} to {self.sell_date.strftime('%Y-%m-%d')}")
        lines.append(f"Total Invested: ${self.total_invested:,.2f}")
        lines.append(f"Final Value: ${self.total_value:,.2f}")

        sign = "+" if self.total_profit >= 0 else ""
        lines.append(f"Total Return: {sign}${self.total_profit:,.2f} ({sign}{self.percent_return:.1f}%)")

        if self.annualized_return is not None:
            sign = "+" if self.annualized_return >= 0 else ""
            lines.append(f"Annualized: {sign}{self.annualized_return:.1f}%")

        return "\n".join(lines)


def simulate_portfolio(
    holdings: list[InvestmentResult],
    buy_date: datetime,
    sell_date: datetime,
) -> PortfolioResult:
    """Calculate portfolio totals from individual holdings."""
    total_invested = sum(h.investment_amount for h in holdings)
    total_value = sum(h.final_value for h in holdings)
    total_profit = total_value - total_invested
    percent_return = (total_profit / total_invested) * 100 if total_invested > 0 else 0

    days_held = (sell_date - buy_date).days
    if days_held > 0:
        years_held = days_held / 365.25
        if years_held >= 0.01:
            total_return = total_value / total_invested
            annualized_return = (pow(total_return, 1 / years_held) - 1) * 100
        else:
            annualized_return = None
    else:
        annualized_return = None

    return PortfolioResult(
        holdings=holdings,
        buy_date=buy_date,
        sell_date=sell_date,
        total_invested=total_invested,
        total_value=total_value,
        total_profit=total_profit,
        percent_return=percent_return,
        annualized_return=annualized_return,
    )


@dataclass
class RankingResult:
    """Ranked list of investments by performance."""
    rankings: list[InvestmentResult] = field(default_factory=list)
    buy_date: datetime = None
    sell_date: datetime = None
    amount: float = 0.0

    def __str__(self) -> str:
        lines = [
            "BEST INVESTMENTS",
            f"Period: {self.buy_date.strftime('%Y-%m-%d')} to {self.sell_date.strftime('%Y-%m-%d')}",
            f"Investment: ${self.amount:,.0f} each",
            "=" * 50,
            f"{'Rank':<5} {'Ticker':<8} {'Return':>12} {'Final Value':>14}",
            "-" * 50,
        ]

        for i, r in enumerate(self.rankings, 1):
            sign = "+" if r.percent_return >= 0 else ""
            lines.append(f"{i:<5} {r.ticker:<8} {sign}{r.percent_return:>10.1f}%  ${r.final_value:>12,.0f}")

        lines.append("=" * 50)
        if self.rankings:
            best = self.rankings[0]
            lines.append(f"Best: {best.ticker} ({best.company_name})")

        return "\n".join(lines)


def rank_investments(results: list[InvestmentResult]) -> list[InvestmentResult]:
    """Sort investments by percent return, highest first."""
    return sorted(results, key=lambda r: r.percent_return, reverse=True)
