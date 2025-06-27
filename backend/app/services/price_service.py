from app.services.protocols import PriceProvider
from app.services.providers.alpha_vantage import AlphaVantageProvider
from app.services.providers.binance_provider import BinanceProvider
from app.services.providers.coingecko import CoinGeckoProvider
from app.services.providers.mock_provider import MockProvider
from app.services.providers.yahoo_provider import YahooFinanceProvider

# TODO: Import configuration (e.g., from app.core.config import settings)


class PriceService:
    """Service responsible for providing the configured price provider."""

    def __init__(self):
        # TODO: Read provider choice from configuration (e.g., settings.PRICE_PROVIDER)
        self.provider_name = "coingecko"  # Use CoinGecko for reliable Bitcoin data

        if self.provider_name == "binance":
            self._provider_instance = BinanceProvider()
        elif self.provider_name == "coingecko":
            self._provider_instance = CoinGeckoProvider()
        elif self.provider_name == "yahoo":
            self._provider_instance = YahooFinanceProvider()
        elif self.provider_name == "alpha_vantage":
            self._provider_instance = AlphaVantageProvider()
        elif self.provider_name == "mock":
            self._provider_instance = MockProvider()
        else:
            raise ValueError(
                f"Unsupported price provider configured: {self.provider_name}"
            )

    def get_provider(self) -> PriceProvider:
        """Returns the configured price provider instance."""
        return self._provider_instance


# --- Dependency Injection Helper ---

# Create a single instance of the service to manage provider selection
# This could also be managed via FastAPI's dependency management system
# if more complex state or initialization is needed.
_price_service_instance = PriceService()


def get_price_provider() -> PriceProvider:
    """FastAPI dependency function to get the configured price provider."""
    return _price_service_instance.get_provider()
