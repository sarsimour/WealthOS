// Corresponds to backend/app/schemas/market_data.py -> MarketDataSource
export enum MarketDataSource {
    COINGECKO = "coingecko",
    YAHOO_FINANCE = "yahoo_finance",
    INTERNAL = "internal_calculation",
}

// Corresponds to backend/app/schemas/market_data.py -> PriceType
export enum PriceType {
    TRADE = "trade",
    BID = "bid",
    ASK = "ask",
    NET_ASSET_VALUE = "nav",
    MID = "mid",
}

// Corresponds to backend/app/schemas/market_data.py -> MarketDataPoint
export interface MarketDataPoint {
  asset_internal_id: string;
  timestamp: string; // Keep as string initially, parse if needed
  source: MarketDataSource;
  currency: string;
  market?: string | null; // Optional
  price_type: PriceType;
  value: number;
  open?: number | null; // Optional
  high?: number | null; // Optional
  low?: number | null; // Optional
  close?: number | null; // Optional
  volume?: number | null; // Optional
} 