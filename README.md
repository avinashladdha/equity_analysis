# Stock Return Analysis Project

This project analyzes historical stock data to understand future price movements and potential returns. Ideally used to identify "Target Prices" for stocks based on statistical frequency distributions rather than simple transient peaks.

## Goal
Calculate future 9-month and 12-month "Target Prices" for a list of stocks.
**Logic:** Instead of taking the single highest peak (which might be a transient spike), we find the most frequent price range (modal bin) in the future window and use its average as the target.

## Methodology

### Algorithm
1.  **Window**: Look ahead 9 months and 12 months from a reference `End_Date`.
2.  **Binning**:
    - Extract all `Close` prices in the lookahead window.
    - Create 10 equal-width bins between the Min and Max price of that window.
    - Identify the "Mode Bin" (the bin with the heaviest concentration of daily close prices).
3.  **Target Price**: Calculate the arithmetic mean of all price points falling into the Mode Bin.

This approach filters out "wick" highs and focuses on price levels where the market found sustained value or acceptance.

## Directory Structure
- `analysis_results_filtered.csv`: Input file containing stocks and reference dates.
- `stock_data_downloads/`: Directory containing historical CSV data for each stock symbol.
- `analysis_results_with_future.csv`: **Output file** containing the calculated target prices and percentage increases.
- `calculate_future_returns.py`: Python script implementing the binning and calculation logic.

## Usage
Run the analysis script:
```bash
python3 calculate_future_returns.py
```

## Output Columns
The output CSV includes:
- `Target_Price_9m`: Average price of the most frequent bin in the 9-month window.
- `Increase_9m_Pct`: Percentage increase from `Price_End_Date` to `Target_Price_9m`.
- `Target_Price_12m`: Average price of the most frequent bin in the 12-month window.
- `Increase_12m_Pct`: Percentage increase from `Price_End_Date` to `Target_Price_12m`.

# Walkthrough - Fetch Market Cap and Earnings Data

I have successfully implemented the script to fetch Market Cap and Earnings (Net Income) data for the last 5 years for Nifty 200 companies.

## Changes
### Data Fetching Script
I created [get_mcap_and_eps.py](file:///Users/avinashladdha/___PERSONAL/Finance/stock_data/equity_analysis/get_mcap_and_eps.py) which:
- Reads the input list from `ind_nifty200list.csv`.
- Uses `yfinance` to fetch data for each stock.
- Extracts `marketCap` and annual `Net Income` for the last 5 available years.
- Saves the results to `nifty200_data.csv`.

## Verification Results
### Execution
The script ran successfully and processed all 200 (or so) companies.

### Output Inspection
I verified the output file [nifty200_data.csv](file:///Users/avinashladdha/___PERSONAL/Finance/stock_data/equity_analysis/nifty200_data.csv).
It contains:
- `Company Name`
- `Symbol`
- `Market Cap`
- `Earnings_YYYY` columns (e.g., Earnings_2024, Earnings_2023, etc.)

Example Data:
| Company Name | Symbol | Market Cap | Earnings_2024 | Earnings_2023 |
| :--- | :--- | :--- | :--- | :--- |
| 360 ONE WAM Ltd. | 360ONE | 459,092,426,752 | 8,042,100,000 | 6,579,300,000 |
| ABB India Ltd. | ABB | 1,111,177,297,920 | 18,716,400,000 | 12,420,500,000 |

Note: Some recent IPOs or companies with irregular financial reporting in yfinance might have missing data points, which is expected.

### Earnings Dates and EPS Data
I created [get_earnings_dates.py](file:///Users/avinashladdha/___PERSONAL/Finance/stock_data/equity_analysis/get_earnings_dates.py) which:
- Loops through Nifty 200 list.
- Fetches `earnings_dates` using `yfinance`.
- Saves individual CSV files to `stock_eps` folder.

#### Results
- Created folder: `equity_analysis/stock_eps/`
- Generated CSV files for each company (e.g., [RELIANCE.csv](file:///Users/avinashladdha/___PERSONAL/Finance/stock_data/equity_analysis/stock_eps/RELIANCE.csv)) containing:
    - `Earnings Date`
    - `EPS Estimate`
    - `Reported EPS`
    - `Surprise(%)`
