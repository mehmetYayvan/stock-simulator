# Stock Investment Simulator

A Python CLI tool that simulates historical stock investments. Ever wondered "What if I had invested in Tesla back in 2020?" This tool answers that question.

## Features

- Fetch historical stock prices from Yahoo Finance
- Simulate investments with custom amounts and dates
- Portfolio mode - track multiple stocks at once
- Calculate returns, profit/loss, and annualized performance
- Support for custom sell dates or current price comparison

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stock-simulator.git
cd stock-simulator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the CLI tool
pip install -e .
```

## Usage

### Simulate an Investment

```bash
# What if I invested $1000 in Apple on January 1, 2020?
stock-sim simulate AAPL --date 2020-01-01 --amount 1000
```

Output:
```
Stock: AAPL (Apple Inc.)
Buy Date: 2020-01-01 @ $74.06
Sell Date: 2024-02-04 @ $187.50
Shares: 13.5025

Investment: $1,000.00 -> $2,531.25
Return: +$1,531.25 (+153.1%)
Annualized: +25.8%
```

### Simulate with a Specific Sell Date

```bash
# What if I bought Tesla in 2019 and sold in 2021?
stock-sim simulate TSLA --date 2019-06-01 --amount 5000 --sell-date 2021-01-01
```

### Portfolio Mode

```bash
# Simulate a portfolio with multiple stocks
stock-sim portfolio AAPL:1000 TSLA:500 MSFT:500 --date 2023-01-01
```

Output:
```
PORTFOLIO SUMMARY
=============================================
AAPL: $1,000 -> $2,148 (+114.8%)
TSLA: $500 -> $1,636 (+227.2%)
MSFT: $500 -> $889 (+77.8%)
=============================================
Period: 2023-01-01 to 2026-02-04
Total Invested: $2,000.00
Final Value: $4,673.07
Total Return: +$2,673.07 (+133.7%)
Annualized: +31.6%
```

### Check Current Price

```bash
stock-sim price MSFT
```

## Command Reference

```
stock-sim simulate TICKER [OPTIONS]

Arguments:
  TICKER                Stock ticker symbol (e.g., AAPL, TSLA, MSFT)

Options:
  -d, --date TEXT       Buy date in YYYY-MM-DD format (required)
  -a, --amount FLOAT    Investment amount in dollars (required)
  -s, --sell-date TEXT  Sell date in YYYY-MM-DD format (default: today)
  --help                Show this message and exit
```

## Supported Stocks

Any stock available on Yahoo Finance, including:
- US stocks (AAPL, GOOGL, MSFT, TSLA, etc.)
- ETFs (SPY, QQQ, VTI, etc.)
- International stocks with proper ticker format

## Tech Stack

- **Python 3.10+**
- **yfinance** - Yahoo Finance API wrapper
- **click** - CLI framework
- **pandas** - Data manipulation

## Future Enhancements

- [x] Portfolio mode (multiple stocks)
- [ ] Visualization with charts
- [ ] Compare against S&P 500 benchmark
- [ ] Dollar-cost averaging simulation
- [ ] "Best investment" finder for a time period
- [ ] Export to CSV/PDF

## License

MIT
