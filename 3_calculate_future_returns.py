
import pandas as pd
import os
from datetime import timedelta

# Define paths
BASE_DIR = "/Users/avinashladdha/___PERSONAL/Finance/stock_data"
INPUT_CSV = os.path.join(BASE_DIR, "kp/analysis_results_filtered.csv")
STOCK_DATA_DIR = os.path.join(BASE_DIR, "stock_data_downloads")
OUTPUT_CSV = os.path.join(BASE_DIR, "kp/analysis_results_with_future.csv")

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
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return None

def get_price_on_date(stock_df, date):
    """
    Gets the Close price on the exact date.
    If the date is missing (e.g. weekend), searches for the closest previous date? 
    Instructions ask for "prices on Start_Date, End_Date". 
    Ideally we find exact match or closest PRIOR trading day if we want 'price at that time'.
    However, the input CSV has dates that should theoretically exist in the dataset or be close to it.
    Let's try to find exact or nearest backward fill.
    """
    # Filter for date <= target
    filtered = stock_df[stock_df['Date'] <= date]
    if filtered.empty:
        return None
    # Get the last one (closest to date)
    return filtered.iloc[-1]['Close']

def calculate_future_target_price(stock_df, start_date, months):
    """
    Calculates the target future price based on the most frequent price range (10 bins).
    Returns the average price of the most frequent bin.
    """
    lookahead_days = int(months * 30.5)
    end_window_date = start_date + timedelta(days=lookahead_days)
    
    # Filter data for the window: start_date < Date <= end_window_date
    mask = (stock_df['Date'] > start_date) & (stock_df['Date'] <= end_window_date)
    window_df = stock_df.loc[mask]
    
    if window_df.empty:
        return None
        
    prices = window_df['Close']
    
    if len(prices) == 0:
        return None

    # Calculate 10 bins
    try:
        # cut/histogram logic
        # pandas cut creates bins
        # We want to find the bin with most occurences
        pd_cut = pd.cut(prices, bins=10)
        bin_counts = pd_cut.value_counts()
        
        # Get the interval (bin) with the highest count
        most_freq_bin_interval = bin_counts.idxmax()
        
        # Find all prices that fall into this interval
        # Interval objects work with bitwise overlaps or by constructing a mask
        # But we can just use the 'pd_cut' series which assigns each row to an interval.
        # Filter prices where the assigned bin matches the most frequent bin
        prices_in_bin = prices[pd_cut == most_freq_bin_interval]
        
        if len(prices_in_bin) == 0:
            return None
            
        # Calculate average of these prices
        avg_price = prices_in_bin.mean()
        return avg_price
        
    except Exception as e:
        print(f"Error calculating bin average for window starting {start_date}: {e}")
        return None

def main():
    print("Loading input CSV...")
    results_df = pd.read_csv(INPUT_CSV)
    
    # Convert dates in input df to datetime objects
    results_df['Start_Date'] = pd.to_datetime(results_df['Start_Date'])
    results_df['End_Date'] = pd.to_datetime(results_df['End_Date'])
    
    # New columns - Removed Max_Date as it's an average
    new_columns = [
        'Price_Start_Date', 'Price_End_Date',
        'Target_Price_9m', 'Increase_9m_Pct',
        'Target_Price_12m', 'Increase_12m_Pct'
    ]
    
    for col in new_columns:
        results_df[col] = None 

    print(f"Processing {len(results_df)} rows...")
    
    stock_cache = {}
    
    for index, row in results_df.iterrows():
        symbol = row['Symbol']
        start_date = row['Start_Date']
        end_date = row['End_Date']
        
        if symbol not in stock_cache:
            stock_df = load_stock_data(symbol)
            if stock_df is not None:
                stock_cache[symbol] = stock_df
            else:
                stock_cache[symbol] = None # Mark as missing
        
        stock_df = stock_cache[symbol]
        
        if stock_df is None:
            continue
            
        # 2. Add prices on Start_Date, End_Date
        price_start = get_price_on_date(stock_df, start_date)
        price_end = get_price_on_date(stock_df, end_date)
        
        results_df.at[index, 'Price_Start_Date'] = price_start
        results_df.at[index, 'Price_End_Date'] = price_end
        
        if pd.isna(price_end) or price_end == 0:
            continue
            
        # 3. Add bin-based target prices for next 9 and 12 months
        # 9 Months
        target_price_9m = calculate_future_target_price(stock_df, end_date, 9)
        if target_price_9m is not None:
            results_df.at[index, 'Target_Price_9m'] = target_price_9m
            results_df.at[index, 'Increase_9m_Pct'] = ((target_price_9m - price_end) / price_end) * 100
            
        # 12 Months
        target_price_12m = calculate_future_target_price(stock_df, end_date, 12)
        if target_price_12m is not None:
            results_df.at[index, 'Target_Price_12m'] = target_price_12m
            results_df.at[index, 'Increase_12m_Pct'] = ((target_price_12m - price_end) / price_end) * 100

        if index % 100 == 0:
            print(f"Processed {index} rows...")

    print("Saving results...")
    results_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Done. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
