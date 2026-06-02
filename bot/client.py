"""
Binance Futures Testnet client wrapper.
Handles client creation and low-level API interaction targeting
the USDT-M Futures Testnet at https://testnet.binancefuture.com
"""

import os
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import get_logger

logger = get_logger(__name__)

TESTNET_FUTURES_BASE_URL = "https://testnet.binancefuture.com"


class BinanceTestnetClient:
    """
    Thin wrapper around python-binance's Client, pre-configured for
    the Binance Futures USDT-M Testnet.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        key = api_key or os.getenv("BINANCE_API_KEY", "")
        secret = api_secret or os.getenv("BINANCE_API_SECRET", "")

        if not key or not secret:
            raise ValueError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set "
                "(via environment variables or passed directly)."
            )

        logger.debug("Initialising Binance Futures Testnet client …")
        try:
            self._client = Client(
                api_key=key,
                api_secret=secret,
                testnet=True,         # routes futures endpoints to testnet
            )
            # Override futures base URL explicitly for clarity / future-proofing
            self._client.FUTURES_URL = TESTNET_FUTURES_BASE_URL + "/fapi"
            logger.info("Binance Futures Testnet client initialised successfully.")
        except BinanceRequestException as exc:
            logger.error("Network error while initialising client: %s", exc)
            raise
        except Exception as exc:
            logger.error("Unexpected error while initialising client: %s", exc)
            raise

    # ── Public helpers ──────────────────────────────────────────────────────

    @property
    def raw(self) -> Client:
        """Expose the underlying python-binance Client if needed."""
        return self._client

    def get_symbol_info(self, symbol: str) -> dict:
        """Fetch exchange info for a specific futures symbol."""
        logger.debug("Fetching exchange info for symbol: %s", symbol)
        try:
            info = self._client.futures_exchange_info()
            for s in info.get("symbols", []):
                if s["symbol"] == symbol.upper():
                    return s
            raise ValueError(f"Symbol '{symbol}' not found on Binance Futures Testnet.")
        except BinanceAPIException as exc:
            logger.error("API error fetching symbol info for %s: %s", symbol, exc)
            raise

    def futures_create_order(self, **kwargs) -> dict:
        """
        Place a futures order and return the raw API response.
        All parameters are forwarded directly to the Binance API.
        """
        logger.debug("Placing futures order | params: %s", kwargs)
        try:
            response = self._client.futures_create_order(**kwargs)
            logger.debug("Raw API response: %s", response)
            return response
        except BinanceAPIException as exc:
            logger.error(
                "Binance API error placing order | code=%s | msg=%s",
                exc.code,
                exc.message,
            )
            raise
        except BinanceRequestException as exc:
            logger.error("Network error placing order: %s", exc)
            raise
        except Exception as exc:
            logger.error("Unexpected error placing order: %s", exc)
            raise
