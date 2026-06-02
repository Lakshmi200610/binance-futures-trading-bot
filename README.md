# Binance Futures Testnet Trading Bot

A clean, well-structured Python CLI application for placing orders on the **Binance USDT-M Futures Testnet**.

---

## Features

| Feature | Details |
|---|---|
| **Order Types** | MARKET, LIMIT, STOP_MARKET (bonus) |
| **Sides** | BUY and SELL |
| **Input Method** | CLI arguments *and* interactive guided mode (bonus) |
| **Validation** | Comprehensive input validation with clear error messages |
| **Logging** | Rotating file log + rich coloured console output |
| **Structure** | Separate client / order / validator / CLI layers |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance Testnet client wrapper
│   ├── orders.py            # Order placement logic
│   ├── validators.py        # Input validation helpers
│   └── logging_config.py   # Rotating file + rich console logging
├── logs/
│   ├── market_order.log     # Sample MARKET order log
│   └── limit_order.log      # Sample LIMIT order log
├── cli.py                   # CLI entry point (Typer)
├── requirements.txt
├── .env.example             # Credential template
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.10+
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account with API credentials

### 1 — Clone / download the project

```bash
# If using Git
git clone <your-repo-url>
cd trading_bot
```

### 2 — Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure API credentials

```bash
# Copy the example file and fill in your credentials
cp .env.example .env
```

Edit `.env`:

```
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_api_secret
```

> **How to get testnet credentials:**
> 1. Visit [testnet.binancefuture.com](https://testnet.binancefuture.com)
> 2. Log in with GitHub
> 3. Go to **API Management** → **Generate API Key**

---

## Usage

Run all commands from the `trading_bot/` directory with your virtual environment active.

### Help

```bash
python cli.py --help
python cli.py market --help
python cli.py limit --help
python cli.py stop-market --help
```

---

### Place a MARKET order

```bash
# Buy 0.01 BTC at market price
python cli.py market BTCUSDT BUY 0.01

# Sell 0.05 ETH at market price
python cli.py market ETHUSDT SELL 0.05
```

**Sample output:**
```
┌──────────────────────────────┐
│    Order Request Summary     │
│ Symbol     │ BTCUSDT         │
│ Side       │ BUY             │
│ Order Type │ MARKET          │
│ Quantity   │ 0.01            │
└──────────────────────────────┘

┌──────────────────────────────┐
│        Order Response        │
│ orderId    │ 3851274903      │
│ symbol     │ BTCUSDT         │
│ side       │ BUY             │
│ type       │ MARKET          │
│ origQty    │ 0.01            │
│ executedQty│ 0.01            │
│ avgPrice   │ 42587.30        │
│ status     │ FILLED          │
└──────────────────────────────┘
╔══════════════════════════════════════════════════╗
║ ✓ Order placed successfully! orderId=3851274903  ║
╚══════════════════════════════════════════════════╝
```

---

### Place a LIMIT order

```bash
# Sell 0.01 BTC at $70,000
python cli.py limit BTCUSDT SELL 0.01 --price 70000

# Buy 0.1 ETH at $2,800
python cli.py limit ETHUSDT BUY 0.1 --price 2800
```

---

### Place a STOP_MARKET order (bonus)

```bash
# Stop-market SELL triggered at $65,000
python cli.py stop-market BTCUSDT SELL 0.01 --stop-price 65000
```

---

### Interactive guided mode (bonus)

Walk through each field with prompts and validation:

```bash
python cli.py interactive
```

Example session:

```
  Symbol (e.g. BTCUSDT): BTCUSDT
  Side [BUY/SELL]: BUY
  Order type [MARKET/LIMIT/STOP_MARKET]: LIMIT
  Quantity: 0.01
  Limit price: 60000

  [Order Request Summary displayed]

  Confirm and place order? [y/N]: y
```

---

## Logging

All requests, responses, and errors are logged to **`trading_bot.log`** (rotating, max 5 MB):

```
2024-01-15 10:23:41 | INFO  | bot.orders | Placing MARKET BUY order | symbol=BTCUSDT | qty=0.01
2024-01-15 10:23:42 | DEBUG | bot.client | Raw API response: {'orderId': 3851274903, ...}
2024-01-15 10:23:42 | INFO  | bot.orders | MARKET order placed successfully | orderId=3851274903 | status=FILLED
```

Sample log files for reference are in the `logs/` directory.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `.env` / empty credentials | Clear config error message + tip to copy `.env.example` |
| Invalid symbol / side / quantity | Validation error with descriptive message, no order placed |
| Missing price for LIMIT order | Validation error before any API call |
| Binance API error (e.g. insufficient balance) | API error code + message displayed; logged to file |
| Network failure | Network error panel displayed; logged to file |

---

## Assumptions

1. All orders target the **USDT-M Futures Testnet** at `https://testnet.binancefuture.com`.
2. LIMIT orders use **GTC (Good Till Cancelled)** time-in-force by default.
3. Quantity precision depends on the symbol's `stepSize` on the testnet — use appropriate decimal places (e.g. `0.001` for BTCUSDT).
4. Credentials are stored in a local `.env` file (never committed to version control).
5. The STOP_MARKET order type is the bonus third order type implemented.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `python-binance` | 1.0.19 | Binance REST API client |
| `typer[all]` | 0.12.3 | CLI framework |
| `rich` | 13.7.1 | Pretty terminal output |
| `python-dotenv` | 1.0.1 | Load `.env` credentials |
| `httpx` | 0.27.0 | HTTP transport (used by python-binance) |
