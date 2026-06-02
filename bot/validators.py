"""
Input validation helpers for CLI arguments.
All validators raise typer.BadParameter on failure so Typer surfaces
a clean error message without a stack trace.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional

import typer

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_side(value: str) -> str:
    """Ensure side is BUY or SELL (case-insensitive)."""
    upper = value.strip().upper()
    if upper not in VALID_SIDES:
        raise typer.BadParameter(
            f"Invalid side '{value}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return upper


def validate_order_type(value: str) -> str:
    """Ensure order type is supported (case-insensitive)."""
    upper = value.strip().upper()
    if upper not in VALID_ORDER_TYPES:
        raise typer.BadParameter(
            f"Invalid order type '{value}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return upper


def validate_symbol(value: str) -> str:
    """Normalise symbol to uppercase and ensure it is non-empty."""
    stripped = value.strip().upper()
    if not stripped:
        raise typer.BadParameter("Symbol must not be empty.")
    # Basic sanity: only letters allowed (BTCUSDT, ETHUSDT, …)
    if not stripped.isalpha():
        raise typer.BadParameter(
            f"Symbol '{value}' appears invalid. Expected letters only (e.g., BTCUSDT)."
        )
    return stripped


def validate_quantity(value: str) -> Decimal:
    """Parse and validate quantity as a positive Decimal."""
    try:
        qty = Decimal(str(value))
    except InvalidOperation:
        raise typer.BadParameter(f"Quantity '{value}' is not a valid number.")
    if qty <= 0:
        raise typer.BadParameter(f"Quantity must be greater than zero, got {qty}.")
    return qty


def validate_price(value: Optional[str], required: bool = False) -> Optional[Decimal]:
    """
    Parse and validate price as a positive Decimal.
    If `required=True` and value is None/empty, raises BadParameter.
    """
    if value is None or str(value).strip() == "":
        if required:
            raise typer.BadParameter("Price is required for LIMIT orders.")
        return None
    try:
        price = Decimal(str(value))
    except InvalidOperation:
        raise typer.BadParameter(f"Price '{value}' is not a valid number.")
    if price <= 0:
        raise typer.BadParameter(f"Price must be greater than zero, got {price}.")
    return price


def validate_stop_price(value: Optional[str], required: bool = False) -> Optional[Decimal]:
    """Parse and validate stop price as a positive Decimal."""
    if value is None or str(value).strip() == "":
        if required:
            raise typer.BadParameter("Stop price is required for STOP_MARKET orders.")
        return None
    try:
        price = Decimal(str(value))
    except InvalidOperation:
        raise typer.BadParameter(f"Stop price '{value}' is not a valid number.")
    if price <= 0:
        raise typer.BadParameter(f"Stop price must be greater than zero, got {price}.")
    return price
