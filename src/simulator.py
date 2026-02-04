"""Investment simulation calculations."""

from dataclasses import dataclass
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
