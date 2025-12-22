import pandas as pd
import yfinance as yf
import os

def get_earnings_dates():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, 'ind_nifty200list.csv')
    output_dir = os.path.join(base_dir, 'stock_eps')

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Read input CSV
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: {input_csv} not found.")
        return

    print(f"Fetching earnings dates for {len(df)} companies...")

    for index, row in df.iterrows():
        symbol = row['Symbol']
        ns_symbol = f"{symbol}.NS"
        
        print(f"Processing {index + 1}/{len(df)}: {ns_symbol}")

        try:
            ticker = yf.Ticker(ns_symbol)
            
            # Fetch earnings dates
            # This returns a DataFrame with Date as index, and columns like 'EPS Estimate', 'Reported EPS', 'Surprise(%)'
            earnings_dates = ticker.earnings_dates
            
            if earnings_dates is not None and not earnings_dates.empty:
                # We want to keep the historical dates, eps estimate, reported eps.
                # These are usually the columns provided.
                
                # Save to CSV
                output_file = os.path.join(output_dir, f"{symbol}.csv")
                earnings_dates.to_csv(output_file)
                # print(f"  Saved to {output_file}")
            else:
                print(f"  Warning: No earnings dates found for {symbol}")

        except Exception as e:
            print(f"  Error fetching data for {symbol}: {e}")

    print("Done.")

if __name__ == "__main__":
    get_earnings_dates()
