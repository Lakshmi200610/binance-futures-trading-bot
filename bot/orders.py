"""
Order placement logic for Binance Futures Testnet.
Supports MARKET, LIMIT, and STOP_MARKET orders.
"""

from decimal import Decimal
from typing import Optional

from binance.enums import (
    SIDE_BUY,
    SIDE_SELL,
    ORDER_TYPE_MARKET,
    ORDER_TYPE_LIMIT,
    TIME_IN_FORCE_GTC,
    FUTURE_ORDER_TYPE_STOP_MARKET,
)
from binance.exceptions import BinanceAPIException

from bot.client import BinanceTestnetClient
from bot.logging_config import get_logger

logger = get_logger(__name__)

# ── Side / type resolvers ────────────────────────────────────────────────────

_SIDE_MAP = {
    "BUY": SIDE_BUY,
    "SELL": SIDE_SELL,
}

_TYPE_MAP = {
    "MARKET": ORDER_TYPE_MARKET,
    "LIMIT": ORDER_TYPE_LIMIT,
    "STOP_MARKET": FUTURE_ORDER_TYPE_STOP_MARKET,
}


# ── Order builders ───────────────────────────────────────────────────────────

def place_market_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: Decimal,
) -> dict:
    """
    Place a MARKET order on Binance Futures Testnet.

    Parameters
    ----------
    client   : BinanceTestnetClient instance
    symbol   : e.g. 'BTCUSDT'
    side     : 'BUY' or 'SELL'
    quantity : order quantity (contracts)

    Returns
    -------
    Parsed order response dict.
    """
    logger.info(
        "Placing MARKET %s order | symbol=%s | qty=%s",
        side, symbol, quantity,
    )

    params = {
        "symbol": symbol,
        "side": _SIDE_MAP[side],
        "type": _TYPE_MAP["MARKET"],
        "quantity": str(quantity),
    }

    logger.debug("Request params: %s", params)
    response = client.futures_create_order(**params)
    logger.info("MARKET order placed successfully | orderId=%s | status=%s",
                response.get("orderId"), response.get("status"))
    return response


def place_limit_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
) -> dict:
    """
    Place a LIMIT GTC order on Binance Futures Testnet.

    Parameters
    ----------
    client   : BinanceTestnetClient instance
    symbol   : e.g. 'BTCUSDT'
    side     : 'BUY' or 'SELL'
    quantity : order quantity (contracts)
    price    : limit price

    Returns
    -------
    Parsed order response dict.
    """
    logger.info(
        "Placing LIMIT %s order | symbol=%s | qty=%s | price=%s",
        side, symbol, quantity, price,
    )

    params = {
        "symbol": symbol,
        "side": _SIDE_MAP[side],
        "type": _TYPE_MAP["LIMIT"],
        "quantity": str(quantity),
        "price": str(price),
        "timeInForce": TIME_IN_FORCE_GTC,
    }

    logger.debug("Request params: %s", params)
    response = client.futures_create_order(**params)
    logger.info("LIMIT order placed successfully | orderId=%s | status=%s",
                response.get("orderId"), response.get("status"))
    return response


def place_stop_market_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: Decimal,
    stop_price: Decimal,
) -> dict:
    """
    Place a STOP_MARKET order on Binance Futures Testnet (bonus order type).

    Parameters
    ----------
    client     : BinanceTestnetClient instance
    symbol     : e.g. 'BTCUSDT'
    side       : 'BUY' or 'SELL'
    quantity   : order quantity (contracts)
    stop_price : trigger price

    Returns
    -------
    Parsed order response dict.
    """
    logger.info(
        "Placing STOP_MARKET %s order | symbol=%s | qty=%s | stopPrice=%s",
        side, symbol, quantity, stop_price,
    )

    params = {
        "symbol": symbol,
        "side": _SIDE_MAP[side],
        "type": _TYPE_MAP["STOP_MARKET"],
        "quantity": str(quantity),
        "stopPrice": str(stop_price),
    }

    logger.debug("Request params: %s", params)
    response = client.futures_create_order(**params)
    logger.info(
        "STOP_MARKET order placed successfully | orderId=%s | status=%s",
        response.get("orderId"), response.get("status"),
    )
    return response


# ── Response formatter ───────────────────────────────────────────────────────

def format_order_response(response: dict) -> dict:
    """
    Extract the most relevant fields from a raw Binance order response
    and return a clean summary dict.
    """
    return {
        "orderId": response.get("orderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
        "origQty": response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "price": response.get("price"),
        "avgPrice": response.get("avgPrice"),
        "stopPrice": response.get("stopPrice"),
        "status": response.get("status"),
        "timeInForce": response.get("timeInForce"),
        "updateTime": response.get("updateTime"),
    }
