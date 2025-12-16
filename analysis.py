import os
import pandas as pd
from datetime import timedelta

INPUT_FOLDER = "stock_data_downloads"
OUTPUT_FILE = "analysis_results.csv"

def analyze_stock(file_path, symbol):
    results = []
def analyze_stock(file_path, symbol):
    results = []
    try:
        # Read with header=0 to see the first row
        df = pd.read_csv(file_path, header=0)
        
        # Handle yfinance multi-header format
        # Format usually is:
        # Row 0: Price, Close, High, Low, Open, Volume
        # Row 1: Ticker, SYMBOL, SYMBOL...
        # Row 2: Date, NaN, NaN...
        # Row 3+: Data
        
        if 'Price' in df.columns and 'Close' in df.columns:
            # Check if row 1 (index 1) has 'Date' in the first column
            # Note: index 1 corresponds to the 3rd line in the file
            if len(df) > 1 and df.iloc[1, 0] == 'Date':
                # Drop the first two rows (Ticker and Date label)
                df = df.iloc[3:].copy()
                # Rename the first column (which was 'Price') to 'Date'
                df.rename(columns={'Price': 'Date'}, inplace=True)
            elif len(df) > 0 and df.iloc[0, 0] == 'Ticker':
                 # Maybe it's just Ticker row then data?
                 # Let's assume the structure we saw: Data starts at index 2
                 df = df.iloc[2:].copy()
                 df.rename(columns={'Price': 'Date'}, inplace=True)
        
        # If 'Date' is still not a column, maybe it was read correctly as header=2?
        # Let's stick to the manual fix above as it matches the file view.
        
        if 'Date' not in df.columns:
            # Fallback: try reading with header=2
            df = pd.read_csv(file_path, header=2)
            if 'Date' not in df.columns:
                print(f"Skipping {symbol}: 'Date' column not found.")
                return []

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        
        if 'Close' not in df.columns:
             print(f"Skipping {symbol}: 'Close' column not found.")
             return []
             
        # Ensure Close is numeric
        print(df.head())
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df = df.dropna(subset=['Close'])

        # Iterate through dates
        dates = df['Date'].tolist()
        closes = df['Close'].tolist()
        n = len(df)
        
        right = 0
        for left in range(n):
            start_date = dates[left]
            start_price = closes[left]
            
            if start_price == 0:
                continue
                
            target_date = start_date + timedelta(days=180) # Approx 6 months
            
            while right < n and dates[right] < target_date:
                right += 1
            
            if right >= n:
                break
                
            # Check if it's within reasonable range (e.g. < 7 months)
            # If the gap is too large, it means missing data or end of file
            if (dates[right] - start_date).days > 210: # 7 months
                continue
                
            end_date = dates[right]
            end_price = closes[right]
            
            if end_price >= start_price * 1.25:
                is_2020 = False
                # "Highlight if the increase was during the year 2020"
                # We can flag if the window overlaps with 2020
                if start_date.year == 2020 or end_date.year == 2020:
                    is_2020 = True
                elif start_date.year < 2020 and end_date.year > 2020:
                    is_2020 = True
                
                results.append({
                    'Symbol': symbol,
                    'Increased_25_pct': 'Yes',
                    'Start_Date': start_date.strftime('%Y-%m-%d'),
                    'End_Date': end_date.strftime('%Y-%m-%d'),
                    'Percentage_Change': f"{((end_price - start_price) / start_price) * 100:.2f}%",
                    'In_2020': 'Yes' if is_2020 else 'No'
                })

    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        
    return results

def main():
    all_results = []
    
    if not os.path.exists(INPUT_FOLDER):
        print(f"Input folder {INPUT_FOLDER} not found.")
        return

    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.csv')]
    print(f"Found {len(files)} files to analyze.")
    
    for i, file_name in enumerate(files):
        symbol = file_name.replace('.csv', '')
        file_path = os.path.join(INPUT_FOLDER, file_name)
        
        # print(f"[{i+1}/{len(files)}] Analyzing {symbol}...")
        stock_results = analyze_stock(file_path, symbol)
        all_results.extend(stock_results)
        
    # Convert to DataFrame
    if all_results:
        results_df = pd.DataFrame(all_results)
        
        # Filter to reduce noise? 
        # User said "There can be more than one entry".
        # Let's keep all.
        
        # Save to CSV
        results_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Analysis complete. Results saved to {OUTPUT_FILE}")
        print(f"Total entries found: {len(results_df)}")
        
        # Show a preview
        print(results_df.head())
    else:
        print("No matching data found.")

if __name__ == "__main__":
    main()
