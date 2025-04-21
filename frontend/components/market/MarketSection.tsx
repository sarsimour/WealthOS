import React from "react";
import Link from "next/link";
// import { Button } from "@/components/ui/button"; // Example Shadcn component

interface MarketSectionProps {
  title: string;
  children: React.ReactNode;
  seeMoreHref?: string; // Optional link to a dedicated page
  className?: string; // Allow passing additional classes
}

const MarketSection: React.FC<MarketSectionProps> = ({ title, children, seeMoreHref, className = '' }) => {
  return (
    <section className={`py-6 md:py-8 ${className}`}>
      <div className="mb-4 flex items-center justify-between">
        {seeMoreHref ? (
          <Link href={seeMoreHref} className="group">
            <h2 className="text-xl font-semibold tracking-tight group-hover:text-primary flex items-center">
              {title}
              <span className="ml-2 transition-transform group-hover:translate-x-1 text-primary">&gt;</span>
            </h2>
          </Link>
        ) : (
          <h2 className="text-xl font-semibold tracking-tight">
            {title}
          </h2>
        )}
        {/* Optional: Keep the 'See all' link on the right if needed, but TradingView uses the title link style */}
        {/* {seeMoreHref && (
          <Link
            href={seeMoreHref}
            className="text-sm font-medium text-primary hover:underline"
          >
            See all
          </Link>
        )} */}
      </div>
      <div className="space-y-4">
        {children}
      </div>
    </section>
  );
};

export default MarketSection; 