"""Tests for simulator module."""

import pytest
from datetime import datetime
from src.simulator import (
    simulate_investment,
    simulate_portfolio,
    rank_investments,
    InvestmentResult,
    PortfolioResult,
    RankingResult,
    BenchmarkResult,
    DCAResult,
)


class TestSimulateInvestment:
    """Tests for simulate_investment function."""

    def test_basic_profit(self):
        """Test basic profitable investment."""
        result = simulate_investment(
            ticker="AAPL",
            company_name="Apple Inc.",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=150.0,
            investment_amount=1000.0,
        )

        assert result.ticker == "AAPL"
        assert result.shares == 10.0
        assert result.final_value == 1500.0
        assert result.profit == 500.0
        assert result.percent_return == 50.0

    def test_basic_loss(self):
        """Test investment with loss."""
        result = simulate_investment(
            ticker="TSLA",
            company_name="Tesla Inc.",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=80.0,
            investment_amount=1000.0,
        )

        assert result.shares == 10.0
        assert result.final_value == 800.0
        assert result.profit == -200.0
        assert result.percent_return == -20.0

    def test_fractional_shares(self):
        """Test calculation with fractional shares."""
        result = simulate_investment(
            ticker="GOOGL",
            company_name="Alphabet Inc.",
            buy_date=datetime(2020, 1, 1),
            buy_price=150.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=200.0,
            investment_amount=1000.0,
        )

        assert result.shares == pytest.approx(6.6667, rel=0.01)
        assert result.final_value == pytest.approx(1333.33, rel=0.01)

    def test_annualized_return_one_year(self):
        """Test annualized return for exactly one year."""
        result = simulate_investment(
            ticker="TEST",
            company_name="Test Co",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=150.0,
            investment_amount=1000.0,
        )

        # 50% return over ~1 year should be ~50% annualized
        assert result.annualized_return is not None
        assert result.annualized_return == pytest.approx(50.0, rel=0.05)

    def test_annualized_return_short_period(self):
        """Test that very short periods don't have annualized return."""
        result = simulate_investment(
            ticker="TEST",
            company_name="Test Co",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2020, 1, 2),
            sell_price=101.0,
            investment_amount=1000.0,
        )

        # 1 day is too short for meaningful annualized return
        assert result.annualized_return is None

    def test_zero_day_holding(self):
        """Test same-day buy and sell."""
        result = simulate_investment(
            ticker="TEST",
            company_name="Test Co",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2020, 1, 1),
            sell_price=100.0,
            investment_amount=1000.0,
        )

        assert result.annualized_return is None


class TestSimulatePortfolio:
    """Tests for simulate_portfolio function."""

    def test_portfolio_totals(self):
        """Test portfolio calculates correct totals."""
        holdings = [
            simulate_investment(
                ticker="AAPL",
                company_name="Apple",
                buy_date=datetime(2020, 1, 1),
                buy_price=100.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=150.0,
                investment_amount=1000.0,
            ),
            simulate_investment(
                ticker="MSFT",
                company_name="Microsoft",
                buy_date=datetime(2020, 1, 1),
                buy_price=200.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=250.0,
                investment_amount=500.0,
            ),
        ]

        result = simulate_portfolio(
            holdings=holdings,
            buy_date=datetime(2020, 1, 1),
            sell_date=datetime(2021, 1, 1),
        )

        assert result.total_invested == 1500.0
        assert result.total_value == 1500.0 + 625.0  # 1500 + 625 = 2125
        assert result.total_profit == 625.0

    def test_portfolio_percent_return(self):
        """Test portfolio percent return calculation."""
        holdings = [
            simulate_investment(
                ticker="TEST",
                company_name="Test",
                buy_date=datetime(2020, 1, 1),
                buy_price=100.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=200.0,
                investment_amount=1000.0,
            ),
        ]

        result = simulate_portfolio(
            holdings=holdings,
            buy_date=datetime(2020, 1, 1),
            sell_date=datetime(2021, 1, 1),
        )

        assert result.percent_return == 100.0


class TestRankInvestments:
    """Tests for rank_investments function."""

    def test_ranking_order(self):
        """Test that investments are ranked by return, highest first."""
        results = [
            simulate_investment(
                ticker="LOW",
                company_name="Low",
                buy_date=datetime(2020, 1, 1),
                buy_price=100.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=110.0,
                investment_amount=1000.0,
            ),
            simulate_investment(
                ticker="HIGH",
                company_name="High",
                buy_date=datetime(2020, 1, 1),
                buy_price=100.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=200.0,
                investment_amount=1000.0,
            ),
            simulate_investment(
                ticker="MID",
                company_name="Mid",
                buy_date=datetime(2020, 1, 1),
                buy_price=100.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=150.0,
                investment_amount=1000.0,
            ),
        ]

        ranked = rank_investments(results)

        assert ranked[0].ticker == "HIGH"
        assert ranked[1].ticker == "MID"
        assert ranked[2].ticker == "LOW"

    def test_ranking_with_losses(self):
        """Test ranking includes negative returns."""
        results = [
            simulate_investment(
                ticker="LOSS",
                company_name="Loss",
                buy_date=datetime(2020, 1, 1),
                buy_price=100.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=50.0,
                investment_amount=1000.0,
            ),
            simulate_investment(
                ticker="GAIN",
                company_name="Gain",
                buy_date=datetime(2020, 1, 1),
                buy_price=100.0,
                sell_date=datetime(2021, 1, 1),
                sell_price=120.0,
                investment_amount=1000.0,
            ),
        ]

        ranked = rank_investments(results)

        assert ranked[0].ticker == "GAIN"
        assert ranked[1].ticker == "LOSS"
        assert ranked[1].percent_return == -50.0


class TestInvestmentResultStr:
    """Tests for InvestmentResult string formatting."""

    def test_str_contains_key_info(self):
        """Test string output contains important information."""
        result = simulate_investment(
            ticker="AAPL",
            company_name="Apple Inc.",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=150.0,
            investment_amount=1000.0,
        )

        output = str(result)

        assert "AAPL" in output
        assert "Apple Inc." in output
        assert "2020-01-01" in output
        assert "1,000" in output or "1000" in output
        assert "50" in output  # percent return


class TestBenchmarkResult:
    """Tests for BenchmarkResult."""

    def test_beat_market(self):
        """Test output when investment beats the market."""
        investment = simulate_investment(
            ticker="AAPL",
            company_name="Apple",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=200.0,
            investment_amount=1000.0,
        )

        benchmark = simulate_investment(
            ticker="SPY",
            company_name="S&P 500",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=120.0,
            investment_amount=1000.0,
        )

        result = BenchmarkResult(investment=investment, benchmark=benchmark)
        output = str(result)

        assert "BEAT" in output
        assert "80" in output  # difference is 80%

    def test_underperform_market(self):
        """Test output when investment underperforms the market."""
        investment = simulate_investment(
            ticker="FAIL",
            company_name="Fail Co",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=105.0,
            investment_amount=1000.0,
        )

        benchmark = simulate_investment(
            ticker="SPY",
            company_name="S&P 500",
            buy_date=datetime(2020, 1, 1),
            buy_price=100.0,
            sell_date=datetime(2021, 1, 1),
            sell_price=120.0,
            investment_amount=1000.0,
        )

        result = BenchmarkResult(investment=investment, benchmark=benchmark)
        output = str(result)

        assert "UNDERPERFORMED" in output


class TestDCAResult:
    """Tests for DCAResult."""

    def test_dca_str_output(self):
        """Test DCA result string contains key info."""
        result = DCAResult(
            ticker="AAPL",
            company_name="Apple Inc.",
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2021, 1, 1),
            amount_per_period=500.0,
            num_purchases=12,
            total_invested=6000.0,
            total_shares=50.0,
            final_value=7500.0,
            profit=1500.0,
            percent_return=25.0,
            avg_cost_per_share=120.0,
            current_price=150.0,
        )

        output = str(result)

        assert "AAPL" in output
        assert "500" in output
        assert "12" in output
        assert "6,000" in output or "6000" in output
        assert "25" in output
