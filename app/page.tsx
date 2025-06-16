'use client';

import React, { useEffect, useState } from 'react';

interface PriceResponse {
  identifier: string;
  currency: string;
  price: number;
}

export default function HomePage() {
  const [btcPrice, setBtcPrice] = useState<PriceResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBtcPrice() {
      try {
        // Assuming the backend is running on localhost:8000
        const response = await fetch('http://localhost:8000/api/v1/prices/crypto/btc?vs_currency=usd');
        if (!response.ok) {
          throw new Error(`Error: ${response.status} ${response.statusText}`);
        }
        const data: PriceResponse = await response.json();
        setBtcPrice(data);
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('An unknown error occurred');
        }
      } finally {
        setIsLoading(false);
      }
    }

    fetchBtcPrice();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">WealthOS</h1>
      <div className="text-2xl">
        {isLoading && <p>Loading Bitcoin price...</p>}
        {error && <p className="text-red-500">Error fetching price: {error}</p>}
        {btcPrice && (
          <p>
            Current Bitcoin (BTC) Price: ${btcPrice.price.toLocaleString()}
          </p>
        )}
      </div>
    </main>
  );
} 