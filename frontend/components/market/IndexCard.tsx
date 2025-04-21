import React from 'react';
import { Card, CardContent } from "@/components/ui/card"; // Assuming Shadcn Card
import { cn } from "@/lib/utils"; // Assuming Shadcn utils path

interface IndexCardProps {
  symbol: string; // e.g., '500', '100'
  name: string; // e.g., 'S&P 500'
  value: number;
  currency: string; // e.g., 'USD'
  changePercent: number; // e.g., 0.13, -1.33
  colorClass?: string; // Optional background for the symbol circle e.g., 'bg-red-500'
}

const IndexCard: React.FC<IndexCardProps> = ({ 
  symbol,
  name,
  value,
  currency,
  changePercent,
  colorClass = 'bg-muted' // Default background color
}) => {
  const isPositive = changePercent >= 0;
  const changeColor = isPositive ? 'text-green-600' : 'text-red-600';
  const changeSign = isPositive ? '+' : '';

  return (
    <Card className="min-w-[180px] flex-shrink-0 snap-start cursor-pointer hover:shadow-md transition-shadow">
      <CardContent className="p-3">
        <div className="flex items-center gap-2 mb-1">
          <div className={cn("h-6 w-6 rounded-full flex items-center justify-center text-xs font-medium text-white", colorClass)}>
            {symbol}
          </div>
          <p className="text-sm font-medium text-foreground truncate">{name}</p>
        </div>
        <div className="text-sm">
          <span className="font-semibold text-foreground">{value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          <span className="text-xs text-muted-foreground ml-1">{currency}</span>
        </div>
        <div className={cn("text-xs font-medium", changeColor)}>
          {changeSign}{changePercent.toFixed(2)}%
        </div>
      </CardContent>
    </Card>
  );
};

export default IndexCard; 