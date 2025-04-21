# Frontend Structure: TradingView-Inspired Market Page

This document outlines the intended structure and principles for the frontend market overview page, aiming to emulate the look, feel, and data presentation style of TradingView's market page (`https://www.tradingview.com/markets/`).

## 1. Core Principles

*   **Modularity:** Build the page using distinct, reusable sections for different market categories (Indices, Stocks, Crypto, etc.).
*   **Data Density & Clarity:** Present key market information concisely using tables, lists, and highlights. Avoid clutter while providing essential data points.
*   **Discoverability:** Offer previews of data within sections and provide clear "See all" or "More" links to dedicated pages for deeper exploration.
*   **Responsiveness:** Ensure a seamless experience across all screen sizes (mobile, tablet, desktop) using mobile-first responsive design techniques (Tailwind CSS breakpoints).
*   **Visual Appeal:** Utilize a clean, modern UI aesthetic similar to TradingView, leveraging Shadcn UI components and Tailwind CSS for styling.
*   **Performance:** Optimize for fast loading times, potentially using Next.js features like Server Components (RSC) for initial data fetching and static generation where applicable.

## 2. Overall Layout Structure

The page follows a standard web layout:

```
<AppLayout>
  <Header />      {/* Persistent navigation, search, user actions */}
  <Main>        {/* Primary content area, vertically scrollable */}
    {/* Market Sections */}
  </Main>
  <Footer />      {/* Site links, legal info, app downloads */}
</AppLayout>
```

*   **`AppLayout`**: The root layout component providing the basic HTML structure, likely including context providers (e.g., ThemeProvider for Shadcn UI).
*   **`Header`**: Contains global navigation, search functionality, and user-related actions (login/signup).
*   **`Main`**: The container for the primary page content, organized into modular market sections.
*   **`Footer`**: Includes site-wide links, copyright information, and potentially links to mobile apps or other resources.

## 3. Main Content Structure: Market Sections

The `<Main>` area is composed of multiple `MarketSection` components, each dedicated to a specific asset class or data category.

```
<Main>
  <HeroSection title="Markets Overview" /> {/* Optional introductory section */}

  <MarketSection title="Indices">
    <IndexListComponent data={...} />
    <SeeMoreLink href="/markets/indices" />
  </MarketSection>

  <MarketSection title="US Stocks">
    <StockHighlightsComponent data={...} />
    <StockDataTable title="Highest Volume" data={...} />
    {/* Other stock components: Volatility, Gainers, Losers, Earnings */}
    <SeeMoreLink href="/markets/us-stocks" />
  </MarketSection>

  <MarketSection title="Crypto">
    {/* Placeholder - Requires Backend Expansion */}
    <CryptoRankingTable title="Market Cap Ranking" data={/* Static or fetched */} />
    {/* Other crypto components: Gainers, Losers, TVL */}
    <SeeMoreLink href="/markets/crypto" />
  </MarketSection>

  {/* Additional sections for World Stocks, Forex, Bonds, etc. */}

</Main>
```

*   **`MarketSection`**: A reusable wrapper component taking a `title` prop and rendering specific data components as children. It provides consistent styling and structure for each market category.
*   **Data Display Components**: Specific components are needed for rendering different data types within sections (e.g., `IndexListComponent`, `StockDataTable`, `CryptoRankingTable`, `EarningsCalendar`, `DataCard`). These components will handle formatting and presentation.
*   **`SeeMoreLink`**: A simple component providing navigation to more detailed pages for each market category.

## 4. Technology Stack

*   **Framework:** Next.js (App Router)
*   **Language:** TypeScript
*   **UI Library:** React
*   **Styling:** Tailwind CSS
*   **Component Library:** Shadcn UI (leveraging Radix UI primitives)
*   **State Management:** Zustand or React Query (TanStack Query) for client-side state and caching if needed.
*   **Data Fetching:** Primarily Server Components for initial load; Client Components with React Query/SWR for dynamic updates or user interactions.

## 5. Backend Integration Notes

*   The current backend provides limited endpoints (e.g., fetching a single crypto price).
*   To fully realize the TradingView-style market overview, the backend will need significant expansion to provide endpoints for:
    *   Lists/rankings of assets (e.g., top stocks by volume, top cryptos by market cap).
    *   Market gainers and losers.
    *   Time-series data for previews/charts (if added later).
    *   Economic and earnings calendar data.
*   Frontend components requiring such data should initially use static placeholders or mock data until backend endpoints are available. Clearly comment on required backend data structures.

## 6. Development Workflow

*   Develop components modularly.
*   Prioritize responsiveness from the start.
*   Fetch data efficiently using Next.js patterns (Server Components preferred).
*   Ensure consistent styling using Tailwind and Shadcn UI.
*   Write tests for key components and data transformations. 