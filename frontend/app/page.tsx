'use client'; // Needed for recharts library

import React, { useEffect, useState } from 'react';
import MarketSection from "@/components/market/MarketSection";
import IndexCard from "@/components/market/IndexCard";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { getLatestCryptoData } from "@/lib/market-api"; // Import the fetch function
import { MarketDataPoint } from "@/types/market-data"; // Import the type
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'; // Import chart components
// Import specific data components when created, e.g.:
// import CryptoRankingTable from "@/components/market/CryptoRankingTable";

// --- Placeholder Index Data ---
const placeholderIndexData = [
  {
    symbol: "500",
    name: "S&P 500",
    value: 5282.69,
    currency: "USD",
    changePercent: 0.13,
    colorClass: "bg-red-600",
  },
  {
    symbol: "100",
    name: "Nasdaq 100",
    value: 18258.09,
    currency: "USD",
    changePercent: 0.00,
    colorClass: "bg-blue-600",
  },
  {
    symbol: "30",
    name: "Dow 30",
    value: 39142.24,
    currency: "USD",
    changePercent: -1.33,
    colorClass: "bg-sky-600",
  },
   {
    symbol: "2000",
    name: "US 2000 small cap",
    value: 1865.621,
    currency: "USD",
    changePercent: -1.08,
    colorClass: "bg-purple-600",
  },
  // Add more placeholder indices...
];

// --- Placeholder Chart Data (for demo structure) ---
const placeholderChartData = [
  { name: 'Jan', uv: 4000 },
  { name: 'Feb', uv: 3000 },
  { name: 'Mar', uv: 2000 },
  { name: 'Apr', uv: 2780 },
  { name: 'May', uv: 1890 },
  { name: 'Jun', uv: 2390 },
  { name: 'Jul', uv: 3490 },
];
// --- End Placeholders ---

// Map display names/symbols to API symbols
const cryptoSymbolsToFetch = [
  { apiSymbol: 'btc', displayName: 'Bitcoin', displaySymbol: 'BTC' },
  { apiSymbol: 'eth', displayName: 'Ethereum', displaySymbol: 'ETH' },
  // Add SOL or others if needed, requires mapping in backend/crypto.py COINGECKO_ID_MAP
  // { apiSymbol: 'sol', displayName: 'Solana', displaySymbol: 'SOL' }, 
];

// Function to format large numbers (Market Cap)
const formatMarketCap = (value: number): string => {
  if (value >= 1e12) {
    return `$${(value / 1e12).toFixed(2)}T`;
  }
  if (value >= 1e9) {
    return `$${(value / 1e9).toFixed(2)}B`;
  }
  if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(2)}M`;
  }
  return `$${value.toFixed(2)}`;
};
// --- End Placeholder Data ---

export default function MarketsPage() {
  // State to hold fetched crypto data
  const [cryptoData, setCryptoData] = useState<(MarketDataPoint & { displayName: string, displaySymbol: string })[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const promises = cryptoSymbolsToFetch.map(async (cryptoInfo) => {
        const data = await getLatestCryptoData(cryptoInfo.apiSymbol, 'USD');
        return data ? { ...data, displayName: cryptoInfo.displayName, displaySymbol: cryptoInfo.displaySymbol } : null;
      });
      
      const results = await Promise.all(promises);
      setCryptoData(results.filter((item): item is MarketDataPoint & { displayName: string, displaySymbol: string } => item !== null));
      setIsLoading(false);
    };

    fetchData();
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div className="container mx-auto px-4">
      <section className="py-8 md:py-12 text-center">
        <h1 className="text-3xl font-bold tracking-tight md:text-5xl lg:text-6xl">
          Markets, everywhere
          {/* Optional: Add dropdown icon */}
        </h1>
        {/* Removed subheading for closer match */}
      </section>

      {/* --- Indices Section (with Horizontal Scroll) --- */}
      <MarketSection title="Indices" seeMoreHref="/markets/indices">
        <div className="relative">
          {/* Add scroll buttons if needed later */}
          <div className="flex space-x-4 overflow-x-auto pb-4 scrollbar-hide snap-x snap-mandatory">
            {placeholderIndexData.map((index) => (
              <IndexCard key={index.name} {...index} />
            ))}
          </div>
        </div>
      </MarketSection>

      {/* --- Chart Section --- */}
      <section className="py-8 md:py-12">
        <div className="h-64 md:h-96 bg-card border rounded-lg p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={placeholderChartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <Line type="monotone" dataKey="uv" stroke="#8884d8" strokeWidth={2} dot={false} />
              <XAxis dataKey="name" axisLine={false} tickLine={false} fontSize={12} />
              <YAxis axisLine={false} tickLine={false} fontSize={12} orientation="right" />
              <Tooltip />
              {/* <CartesianGrid stroke="#ccc" strokeDasharray="5 5" vertical={false} /> */}
            </LineChart>
          </ResponsiveContainer>
        </div>
        {/* Placeholder for chart controls */}
        <div className="mt-4 flex justify-between items-center">
          <div className="flex gap-2">
            {/* Time range buttons (e.g., 1D, 1M) */}
          </div>
          <div className="flex gap-2">
            {/* Chart icons (e.g., settings, fullscreen) */}
          </div>
        </div>
      </section>

      {/* --- Crypto Section (Data Fetched) --- */}
      <MarketSection title="Cryptocurrencies" seeMoreHref="/markets/crypto">
        <div className="overflow-hidden rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[200px]">Name</TableHead>
                <TableHead className="text-right">Price</TableHead>
                {/* Add 24h Change header if data becomes available */}
                {/* <TableHead className="text-right">24h %</TableHead> */}
                <TableHead className="text-right">Timestamp</TableHead> {/* Example: show timestamp */}
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={3} className="h-24 text-center text-muted-foreground">
                    Loading crypto data...
                  </TableCell>
                </TableRow>
              ) : cryptoData.length > 0 ? (
                cryptoData.map((crypto) => (
                  <TableRow key={crypto.asset_internal_id}>
                    <TableCell className="font-medium">
                      {crypto.displayName} <span className="ml-1 text-muted-foreground text-xs">{crypto.displaySymbol}</span>
                    </TableCell>
                    <TableCell className="text-right">${crypto.value.toFixed(2)}</TableCell>
                    {/* Placeholder for 24h Change - Needs backend data */}
                    {/* <TableCell className={"text-right"}> TBD% </TableCell> */}
                    <TableCell className="text-right text-xs text-muted-foreground">
                      {new Date(crypto.timestamp).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={3} className="h-24 text-center text-muted-foreground">
                    No crypto data available or failed to load.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </MarketSection>

      {/* --- Placeholder for World Indices --- */}
      <MarketSection title="World Indices" seeMoreHref="/markets/world-indices">
        <div className="h-24 bg-muted rounded-lg flex items-center justify-center text-muted-foreground italic">
          World Indices Cards Placeholder (Horizontal Scroll)
        </div>
      </MarketSection>

      {/* --- Placeholder for US Stocks Section --- */}
      <MarketSection title="US Stocks" seeMoreHref="/markets/us-stocks">
        <div className="h-24 bg-muted rounded-lg flex items-center justify-center text-muted-foreground italic">
          US Stocks Data Placeholder (Tables/Cards)
        </div>
      </MarketSection>

    </div>
  );
} 