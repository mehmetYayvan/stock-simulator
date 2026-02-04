# Stock Investment Simulator

A Python CLI tool that simulates historical stock investments. Ever wondered "What if I had invested in Tesla back in 2020?" This tool answers that question.

## Features

- Simulate stock/ETF/crypto/currency investments
- Portfolio mode - track multiple assets
- Best investment finder - rank by performance
- Compare scenarios - what if A vs B?
- Calculate returns, profit/loss, annualized performance

## Installation

```bash
git clone https://github.com/mehmetYayvan/stock-simulator.git
cd stock-simulator
pip install -r requirements.txt
pip install -e .
```

## Usage

```bash
# Single stock simulation
python -m src.cli simulate AAPL --date 2020-01-01 --amount 1000

# Portfolio (multiple stocks)
python -m src.cli portfolio AAPL:1000 TSLA:500 MSFT:500 --date 2023-01-01

# Find best performers
python -m src.cli best AAPL TSLA MSFT GOOGL NVDA --date 2020-01-01 --top 5

# Compare scenarios
python -m src.cli compare "AAPL:1000,TSLA:500" "MSFT:800,GOOGL:700" --date 2020-01-01

# Current price
python -m src.cli price TSLA

# Currencies & crypto (use =X suffix)
python -m src.cli simulate EURUSD=X --date 2020-01-01 --amount 1000
python -m src.cli simulate BTC-USD --date 2020-01-01 --amount 1000
```

## Supported Assets

- US stocks: AAPL, TSLA, MSFT, GOOGL, etc.
- ETFs: SPY, QQQ, VTI, etc.
- Crypto: BTC-USD, ETH-USD, etc.
- Currencies: EURUSD=X, GBPUSD=X, etc.

## Tech Stack

Python 3.10+ | yfinance | click | pandas

## Future Enhancements

- [x] Portfolio mode
- [x] Best investment finder
- [x] Compare scenarios
- [ ] Visualization with charts
- [ ] Compare against S&P 500 benchmark
- [ ] Dollar-cost averaging simulation

## License

MIT
