
import pandas as pd
import os
from datetime import timedelta
import numpy as np

# Define paths
BASE_DIR = "/Users/avinashladdha/___PERSONAL/Finance/stock_data"
INPUT_CSV = os.path.join(BASE_DIR, "equity_analysis/analysis_results_with_future.csv")
STOCK_DATA_DIR = os.path.join(BASE_DIR, "stock_data_downloads")
MCAP_CSV = os.path.join(BASE_DIR, "equity_analysis/nifty200_data.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "equity_analysis/analysis_results_final.csv")

def load_stock_data(symbol):
    """
    Loads stock data for a given symbol.
    Skips the first 3 rows of headers and assigns standardized column names.
    """
    file_path = os.path.join(STOCK_DATA_DIR, f"{symbol}.csv")
    if not os.path.exists(file_path):
        return None
    
    try:
        # Skip the first 3 rows which contain metadata/multi-index headers
        df = pd.read_csv(file_path, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
        # Handle cases where skiprows might be different or headers are different?
        # The view_file of previous script showed this logic works.
        # Let's add basic validation if Date column is not dates
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        return df.sort_values('Date')
    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return None

def get_price_on_date(stock_df, date, direction='backward'):
    """
    Gets the Close price on the exact date.
    If the date is missing:
    - direction='backward': searches for the closest previous date (for past dates)
    - direction='forward': searches for the closest next date (for future dates? No, usually we want known prices)
    Actually for stock prices, usually we want the last available closing price if exact date is a holiday.
    So 'backward' (pad) is generally correct.
    """
    if pd.isna(date):
        return None
        
    # Convert date to datetime if not already
    date = pd.to_datetime(date)
    
    # Filter for date (exact or before)
    filtered = stock_df[stock_df['Date'] <= date]
    if filtered.empty:
        # Try looking a bit forward if it's start of data? rare.
        return None
    # Get the last one (closest to date from left)
    return filtered.iloc[-1]['Close']

def calculate_cagr(start_price, end_price, years):
    if start_price is None or end_price is None or start_price <= 0 or end_price <= 0:
        return None
    try:
        cagr = (end_price / start_price) ** (1 / years) - 1
        return cagr * 100  # Return as percentage
    except:
        return None

def main():
    print("Loading data...")
    results_df = pd.read_csv(INPUT_CSV)
    mcap_df = pd.read_csv(MCAP_CSV)
    
    # Create Market Cap map
    # Ensure Symbol columns match
    mcap_map = dict(zip(mcap_df['Symbol'], mcap_df['Market Cap']))
    
    # Convert dates in results_df
    results_df['End_Date'] = pd.to_datetime(results_df['End_Date'])
    
    # Initialize new columns
    new_cols = [
        'CAGR_Prev_3yr', 'CAGR_Prev_5yr',
        'CAGR_Fwd_1yr', 'CAGR_Fwd_3yr', 'CAGR_Fwd_5yr',
        'Market_Cap'
    ]
    for col in new_cols:
        results_df[col] = None
        
    print(f"Processing {len(results_df)} rows...")
    
    stock_cache = {}
    
    for index, row in results_df.iterrows():
        symbol = row['Symbol']
        end_date = row['End_Date']
        
        # 1. Market Cap
        if symbol in mcap_map:
            results_df.at[index, 'Market_Cap'] = mcap_map[symbol]
            
        # Load stock data
        if symbol not in stock_cache:
            stock_df = load_stock_data(symbol)
            if stock_df is not None:
                stock_cache[symbol] = stock_df
            else:
                stock_cache[symbol] = None
        
        stock_df = stock_cache[symbol]
        
        if stock_df is None:
            continue
            
        # Get Price at End_Date
        # Use existing Price_End_Date if reliable, but better to fetch from loaded df to be sure it matches
        price_end = get_price_on_date(stock_df, end_date)
        if price_end is None:
            continue
            
        # --- Previous CAGR ---
        # 3 Year
        date_prev_3y = end_date - pd.DateOffset(years=3)
        price_prev_3y = get_price_on_date(stock_df, date_prev_3y)
        cagr_3y_prev = calculate_cagr(price_prev_3y, price_end, 3)
        results_df.at[index, 'CAGR_Prev_3yr'] = cagr_3y_prev
        
        # 5 Year
        date_prev_5y = end_date - pd.DateOffset(years=5)
        price_prev_5y = get_price_on_date(stock_df, date_prev_5y)
        cagr_5y_prev = calculate_cagr(price_prev_5y, price_end, 5)
        results_df.at[index, 'CAGR_Prev_5yr'] = cagr_5y_prev
        
        # --- Forward CAGR ---
        # 1 Year
        date_fwd_1y = end_date + pd.DateOffset(years=1)
        price_fwd_1y = get_price_on_date(stock_df, date_fwd_1y)
        cagr_1y_fwd = calculate_cagr(price_end, price_fwd_1y, 1)
        results_df.at[index, 'CAGR_Fwd_1yr'] = cagr_1y_fwd
        
        # 3 Year
        date_fwd_3y = end_date + pd.DateOffset(years=3)
        price_fwd_3y = get_price_on_date(stock_df, date_fwd_3y)
        cagr_3y_fwd = calculate_cagr(price_end, price_fwd_3y, 3)
        results_df.at[index, 'CAGR_Fwd_3yr'] = cagr_3y_fwd
        
        # 5 Year
        date_fwd_5y = end_date + pd.DateOffset(years=5)
        price_fwd_5y = get_price_on_date(stock_df, date_fwd_5y)
        cagr_5y_fwd = calculate_cagr(price_end, price_fwd_5y, 5)
        results_df.at[index, 'CAGR_Fwd_5yr'] = cagr_5y_fwd

        if index % 100 == 0:
            print(f"Processed {index} rows...")

    print("Saving results...")
    results_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Done. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
