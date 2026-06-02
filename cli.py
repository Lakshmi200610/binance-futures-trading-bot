"""
cli.py – Typer-based CLI entry point for the Binance Futures Trading Bot.

Commands
--------
  market      – Place a Market order
  limit       – Place a Limit order
  stop-market – Place a Stop-Market order (bonus)
  interactive – Guided interactive mode (bonus)

Usage examples
--------------
  python cli.py market BTCUSDT BUY 0.01
  python cli.py limit  BTCUSDT SELL 0.01 --price 70000
  python cli.py stop-market BTCUSDT SELL 0.01 --stop-price 65000
  python cli.py interactive
"""

from __future__ import annotations

import os
import sys
from decimal import Decimal
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# ── Bootstrap ────────────────────────────────────────────────────────────────
load_dotenv()  # Load .env before anything that needs env vars

from bot.logging_config import setup_logging, get_logger
from bot.client import BinanceTestnetClient
from bot.orders import (
    place_market_order,
    place_limit_order,
    place_stop_market_order,
    format_order_response,
)
from bot.validators import (
    validate_side,
    validate_symbol,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

# ── Initialise logging & console ─────────────────────────────────────────────
setup_logging()
logger = get_logger(__name__)
console = Console()

app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet – Trading Bot CLI",
    no_args_is_help=True,
)


# ── Shared helpers ────────────────────────────────────────────────────────────

def _get_client() -> BinanceTestnetClient:
    """Initialise and return the testnet client, exiting cleanly on failure."""
    try:
        return BinanceTestnetClient()
    except ValueError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        console.print(
            "[yellow]Tip:[/yellow] Copy [bold].env.example[/bold] to [bold].env[/bold] "
            "and fill in your Binance Futures Testnet API credentials."
        )
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Failed to connect to Binance:[/bold red] {exc}")
        raise typer.Exit(code=1)


def _print_request_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None,
    stop_price: Optional[Decimal] = None,
) -> None:
    """Print a styled summary of the order request."""
    table = Table(
        title="[bold]Order Request Summary[/bold]",
        box=box.ROUNDED,
        show_header=False,
        border_style="cyan",
    )
    table.add_column("Field", style="bold magenta", width=14)
    table.add_column("Value", style="white")

    table.add_row("Symbol", symbol)
    table.add_row("Side", f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]")
    table.add_row("Order Type", order_type)
    table.add_row("Quantity", str(quantity))
    if price is not None:
        table.add_row("Price", str(price))
    if stop_price is not None:
        table.add_row("Stop Price", str(stop_price))

    console.print()
    console.print(table)


def _print_order_response(response: dict) -> None:
    """Print a styled summary of the order response."""
    summary = format_order_response(response)

    table = Table(
        title="[bold]Order Response[/bold]",
        box=box.ROUNDED,
        show_header=False,
        border_style="green",
    )
    table.add_column("Field", style="bold cyan", width=14)
    table.add_column("Value", style="white")

    for key, val in summary.items():
        if val is not None and val != "":
            table.add_row(key, str(val))

    console.print(table)
    console.print(
        Panel(
            f"[bold green]✓ Order placed successfully![/bold green]  "
            f"orderId=[cyan]{summary['orderId']}[/cyan]  "
            f"status=[yellow]{summary['status']}[/yellow]",
            border_style="green",
        )
    )


def _handle_error(exc: Exception) -> None:
    """Print a user-friendly error panel and exit with code 1."""
    from binance.exceptions import BinanceAPIException, BinanceRequestException

    if isinstance(exc, BinanceAPIException):
        msg = f"[bold red]Binance API Error[/bold red] (code {exc.code}): {exc.message}"
    elif isinstance(exc, BinanceRequestException):
        msg = f"[bold red]Network Error:[/bold red] {exc}"
    else:
        msg = f"[bold red]Error:[/bold red] {exc}"

    console.print(Panel(msg, border_style="red", title="[bold red]Order Failed[/bold red]"))
    logger.error("Order failed: %s", exc)
    raise typer.Exit(code=1)


# ── Commands ──────────────────────────────────────────────────────────────────

@app.command()
def market(
    symbol: str = typer.Argument(..., help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Argument(..., help="BUY or SELL"),
    quantity: str = typer.Argument(..., help="Order quantity (number of contracts)"),
) -> None:
    """
    Place a MARKET order on Binance Futures Testnet.

    Example: python cli.py market BTCUSDT BUY 0.01
    """
    sym = validate_symbol(symbol)
    s   = validate_side(side)
    qty = validate_quantity(quantity)

    logger.info("CMD: market | symbol=%s | side=%s | qty=%s", sym, s, qty)
    _print_request_summary(sym, s, "MARKET", qty)

    client = _get_client()
    try:
        response = place_market_order(client, sym, s, qty)
        _print_order_response(response)
    except Exception as exc:
        _handle_error(exc)


@app.command()
def limit(
    symbol: str = typer.Argument(..., help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Argument(..., help="BUY or SELL"),
    quantity: str = typer.Argument(..., help="Order quantity (number of contracts)"),
    price: str = typer.Option(..., "--price", "-p", help="Limit price (required)"),
) -> None:
    """
    Place a LIMIT GTC order on Binance Futures Testnet.

    Example: python cli.py limit BTCUSDT SELL 0.01 --price 70000
    """
    sym   = validate_symbol(symbol)
    s     = validate_side(side)
    qty   = validate_quantity(quantity)
    px    = validate_price(price, required=True)

    logger.info("CMD: limit | symbol=%s | side=%s | qty=%s | price=%s", sym, s, qty, px)
    _print_request_summary(sym, s, "LIMIT", qty, price=px)

    client = _get_client()
    try:
        response = place_limit_order(client, sym, s, qty, px)
        _print_order_response(response)
    except Exception as exc:
        _handle_error(exc)


@app.command(name="stop-market")
def stop_market(
    symbol: str = typer.Argument(..., help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Argument(..., help="BUY or SELL"),
    quantity: str = typer.Argument(..., help="Order quantity (number of contracts)"),
    stop_price: str = typer.Option(..., "--stop-price", "-s", help="Stop trigger price (required)"),
) -> None:
    """
    Place a STOP_MARKET order on Binance Futures Testnet.
    Triggers a market order when the stop price is reached.

    Example: python cli.py stop-market BTCUSDT SELL 0.01 --stop-price 65000
    """
    sym  = validate_symbol(symbol)
    s    = validate_side(side)
    qty  = validate_quantity(quantity)
    sp   = validate_stop_price(stop_price, required=True)

    logger.info(
        "CMD: stop-market | symbol=%s | side=%s | qty=%s | stopPrice=%s",
        sym, s, qty, sp,
    )
    _print_request_summary(sym, s, "STOP_MARKET", qty, stop_price=sp)

    client = _get_client()
    try:
        response = place_stop_market_order(client, sym, s, qty, sp)
        _print_order_response(response)
    except Exception as exc:
        _handle_error(exc)


@app.command()
def interactive() -> None:
    """
    Interactive guided mode – prompts you for each field with validation,
    then places the order.

    Example: python cli.py interactive
    """
    console.print(
        Panel(
            "[bold cyan]Binance Futures Testnet[/bold cyan] – Interactive Order Entry",
            subtitle="Press Ctrl+C to cancel at any time",
            border_style="cyan",
        )
    )

    # ── Symbol ────────────────────────────────────────────────
    while True:
        raw_symbol = typer.prompt("  Symbol (e.g. BTCUSDT)").strip()
        try:
            sym = validate_symbol(raw_symbol)
            break
        except typer.BadParameter as e:
            console.print(f"  [red]✗[/red] {e}")

    # ── Side ──────────────────────────────────────────────────
    while True:
        raw_side = typer.prompt("  Side [BUY/SELL]").strip()
        try:
            s = validate_side(raw_side)
            break
        except typer.BadParameter as e:
            console.print(f"  [red]✗[/red] {e}")

    # ── Order Type ────────────────────────────────────────────
    order_type = None
    while True:
        raw_type = typer.prompt("  Order type [MARKET/LIMIT/STOP_MARKET]").strip().upper()
        if raw_type in ("MARKET", "LIMIT", "STOP_MARKET"):
            order_type = raw_type
            break
        console.print("  [red]✗[/red] Must be MARKET, LIMIT, or STOP_MARKET.")

    # ── Quantity ──────────────────────────────────────────────
    while True:
        raw_qty = typer.prompt("  Quantity").strip()
        try:
            qty = validate_quantity(raw_qty)
            break
        except typer.BadParameter as e:
            console.print(f"  [red]✗[/red] {e}")

    # ── Price (LIMIT only) ────────────────────────────────────
    px = None
    if order_type == "LIMIT":
        while True:
            raw_px = typer.prompt("  Limit price").strip()
            try:
                px = validate_price(raw_px, required=True)
                break
            except typer.BadParameter as e:
                console.print(f"  [red]✗[/red] {e}")

    # ── Stop Price (STOP_MARKET only) ─────────────────────────
    sp = None
    if order_type == "STOP_MARKET":
        while True:
            raw_sp = typer.prompt("  Stop price").strip()
            try:
                sp = validate_stop_price(raw_sp, required=True)
                break
            except typer.BadParameter as e:
                console.print(f"  [red]✗[/red] {e}")

    # ── Confirmation ──────────────────────────────────────────
    _print_request_summary(sym, s, order_type, qty, price=px, stop_price=sp)
    confirm = typer.confirm("\n  Confirm and place order?")
    if not confirm:
        console.print("[yellow]Order cancelled.[/yellow]")
        raise typer.Exit()

    # ── Execute ───────────────────────────────────────────────
    client = _get_client()
    try:
        if order_type == "MARKET":
            logger.info("CMD: interactive MARKET | symbol=%s | side=%s | qty=%s", sym, s, qty)
            response = place_market_order(client, sym, s, qty)
        elif order_type == "LIMIT":
            logger.info("CMD: interactive LIMIT | symbol=%s | side=%s | qty=%s | price=%s", sym, s, qty, px)
            response = place_limit_order(client, sym, s, qty, px)
        else:  # STOP_MARKET
            logger.info("CMD: interactive STOP_MARKET | symbol=%s | side=%s | qty=%s | stopPrice=%s", sym, s, qty, sp)
            response = place_stop_market_order(client, sym, s, qty, sp)

        _print_order_response(response)
    except Exception as exc:
        _handle_error(exc)


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
