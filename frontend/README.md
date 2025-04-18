# WealthOS Frontend

Frontend application for the WealthOS financial analysis and investment platform.

## Setup

### Prerequisites

- Node.js 18 or higher
- pnpm (recommended) or npm

### Installation

1. Install dependencies:

```bash
pnpm install
```

2. Set up environment variables:

```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

3. Run the development server:

```bash
pnpm dev
```

The application will be available at `http://localhost:4300`.

## Development

### Code Formatting

```bash
pnpm format
```

### Linting

```bash
pnpm lint
```

### Building for Production

```bash
pnpm build
```

## Project Structure

- `app/`: Next.js app router
  - `(auth)/`: Authentication routes
  - `dashboard/`: Dashboard routes
  - `portfolio/`: Portfolio routes
  - `market/`: Market analysis routes
  - `reports/`: Reporting routes
  - `settings/`: Settings routes
- `components/`: Reusable components
  - `ui/`: Basic UI components
  - `charts/`: Chart components
  - `tables/`: Table components
  - `forms/`: Form components
  - `layout/`: Layout components
- `lib/`: Frontend utilities
- `hooks/`: Custom React hooks
- `store/`: State management
- `types/`: TypeScript types 