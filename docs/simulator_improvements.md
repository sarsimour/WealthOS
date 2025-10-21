# Investment Simulator Improvements

This document outlines the identified bugs and feature requests for the Investment Simulator, along with the plan to address them.

## 1. Bug: "Current Date" Display Issue

**Problem:** The "Current Date" metric card in the frontend displays a large numerical timestamp instead of a human-readable date.

**Root Cause:** The `Date.parse()` function returns a timestamp (milliseconds since epoch), which is then directly displayed without proper formatting.

**Solution:**
Modify `frontend/src/components/InvestmentSimulator.tsx` to format the timestamp obtained from `currentDisplayData.date` into a user-friendly date string (e.g., "YYYY-MM-DD") before rendering it in the `MetricCard`.

## 2. Bug: "Pause" Button Functionality

**Problem:** The animation's "Pause" button does not work as expected:
- There is a slight delay before the animation actually pauses.
- Clicking "Play" after pausing restarts the animation from the beginning instead of resuming from where it left off.

**Root Cause:**
- The `clearInterval` might not be taking effect immediately, or the state update for `playing` is not synchronized.
- The `startAnimation` function currently resets `currentIndex` to 0.

**Solution:**
Modify `frontend/src/components/InvestmentSimulator.tsx`:
- Ensure `clearInterval(intervalRef.current)` is called synchronously when `pauseAnimation` is triggered.
- Update `startAnimation` to check the current `animationState.currentIndex` and resume from that point if `playing` is false, instead of always resetting to 0.

## 3. Feature Request: Asset Price Change & Return Rate Comparison

**Problem:** The user wants to:
- See a line on the chart representing the asset's price change, normalized to a 0% return rate at the simulation start.
- Display the asset's overall return rate alongside the profit rate in the summary for comparison with the DCA strategy's profit rate.

**Solution:**

### Backend (`app/wealthos/analyzers/period_investment.py`)
- **Review/Modify `period_investment_simulation`:** Ensure the function returns the raw `close_prices` for the simulation period. If it doesn't, modify it to include this data in the `time_series` output. This will be used to calculate the normalized asset price on the frontend.

### Frontend (`frontend/src/components/InvestmentSimulator.tsx`)
- **Calculate Normalized Asset Price:**
    - In the `getChartOptions` function or a helper, calculate a new series for the asset's price change.
    - Normalize this series so that its starting point (first `close_price` in the simulation period) corresponds to a 0% return. Subsequent points will show percentage change relative to the start.
- **Add New Chart Series:**
    - Add this new normalized asset price series to the `series` array in the ECharts `option`.
- **Update Summary:**
    - Calculate the overall return rate of the asset (buy and hold) for the simulation period.
    - Add a new `MetricCard` or update an existing one in the final summary section to display this "Asset Buy & Hold Return Rate".
