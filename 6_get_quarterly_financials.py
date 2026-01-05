import pandas as pd
import yfinance as yf
import os
import time
import random

def get_quarterly_financials():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, 'data', 'ind_nifty200list.csv')
    output_dir = os.path.join(base_dir, 'quarterly_fin')

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

    print(f"Fetching quarterly financials for {len(df)} companies...")

    for index, row in df.iterrows():
        symbol = row['Symbol']
        ns_symbol = f"{symbol}.NS"
        
        print(f"Processing {index + 1}/{len(df)}: {ns_symbol}")

        try:
            ticker = yf.Ticker(ns_symbol)
            
            # Fetch quarterly financials
            # yfinance returns this with Dates as Columns and Metrics as Rows (Index)
            max_retries = 3
            q_financials = None
            
            for attempt in range(max_retries):
                try:
                    q_financials = ticker.quarterly_financials
                    if q_financials is not None and not q_financials.empty:
                        break
                    else:
                        if attempt < max_retries - 1:
                            wait_time = random.uniform(10, 20)
                            print(f"  Warning: Empty financials for {symbol}. Retrying in {wait_time:.1f}s (Attempt {attempt+1}/{max_retries})...")
                            time.sleep(wait_time)
                except Exception as e:
                    if "Too Many Requests" in str(e) and attempt < max_retries - 1:
                        wait_time = random.uniform(30, 60) # Longer wait for 429
                        print(f"  Rate Limited. Waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)
                    else:
                         print(f"  Error on attempt {attempt+1}: {e}")
            
            # Add small random delay between stocks to avoid hitting limits
            time.sleep(random.uniform(2, 5))
            
            if q_financials is not None and not q_financials.empty:
                # Calculate Market Cap
                try:
                    # Fetch history for price (past 5 years to be safe for all quarters returned)
                    hist = ticker.history(period="10y")
                    
                    if not hist.empty and 'Basic Average Shares' in q_financials.index:
                        market_caps = []
                        for date in q_financials.columns:
                            ts = pd.to_datetime(date)
                            
                            # Find closest price (backward look)
                            # hist.index is timezone aware sometimes, timestamps from q_financials are usually not or vice versa
                            # Let's standardize to tz-naive for comparison to be safe
                            ts_naive = ts.tz_localize(None)
                            hist_index_naive = hist.index.tz_localize(None)
                            
                            # Filter prices on or before the date
                            mask = hist_index_naive <= ts_naive
                            valid_hist = hist[mask]
                            
                            if not valid_hist.empty:
                                price = valid_hist.iloc[-1]['Close']
                                shares = q_financials.loc['Basic Average Shares', date]
                                mcap = price * shares
                                market_caps.append(mcap)
                            else:
                                market_caps.append(None)
                        
                        # Add Market Cap row
                        q_financials.loc['Market Cap'] = market_caps
                        
                except Exception as mc_e:
                    print(f"  Warning: Could not calculate Market Cap for {symbol}: {mc_e}")

                # Transpose to have Dates as Index (Rows) to be "similar" to stock_eps data
                q_financials_T = q_financials.T
                
                # Save to CSV
                output_file = os.path.join(output_dir, f"{symbol}.csv")
                q_financials_T.to_csv(output_file)
                # print(f"  Saved to {output_file}")
            else:
                print(f"  Warning: No quarterly financials found for {symbol}")

        except Exception as e:
            print(f"  Error fetching data for {symbol}: {e}")

    print("Done.")

if __name__ == "__main__":
    get_quarterly_financials()
