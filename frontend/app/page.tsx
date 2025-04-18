export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-primary">
            Welcome to WealthOS
          </h1>
          <p className="mt-4 text-xl text-muted-foreground">
            All-in-one platform for financial analysis and investment
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
          <FeatureCard
            title="Data Integration"
            description="Unified access to multiple data sources with standardized validation and cleaning."
          />
          <FeatureCard
            title="Factor Analysis"
            description="Generate and test factors across asset classes for portfolio construction."
          />
          <FeatureCard
            title="Portfolio Management"
            description="Optimize portfolios with advanced risk analysis and management tools."
          />
          <FeatureCard
            title="Market Monitoring"
            description="Real-time market scanning with anomaly detection and opportunity scoring."
          />
          <FeatureCard
            title="AI-Enhanced Analytics"
            description="Leverage predictive modeling, pattern recognition, and NLP for insights."
          />
          <FeatureCard
            title="Reporting"
            description="Customizable dashboards with automated report generation and visualizations."
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="bg-card rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <h3 className="text-lg font-medium text-card-foreground">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  );
} 