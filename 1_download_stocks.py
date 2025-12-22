import os
import pandas as pd
import yfinance as yf
import nselib
from nselib import capital_market as cm
from datetime import datetime, timedelta

# Configuration
OUTPUT_FOLDER = "stock_data_downloads"
YEARS = 10
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=YEARS * 365)

def get_nifty_symbols():
    """
    Attempts to get Nifty 200 symbols. 
    Prioritizes ind_nifty200list.csv, then nifty200.csv, then falls back to Nifty 50.
    """
    symbols = []
    
    # 1. Try reading from ind_nifty200list.csv (User provided)
    if os.path.exists("ind_nifty200list.csv"):
        try:
            print("Found ind_nifty200list.csv...")
            df = pd.read_csv("ind_nifty200list.csv")
            if "Symbol" in df.columns:
                symbols = df["Symbol"].tolist()
                print(f"Retrieved {len(symbols)} symbols from ind_nifty200list.csv.")
                return symbols
            else:
                print("ind_nifty200list.csv found but could not find 'Symbol' column.")
        except Exception as e:
            print(f"Error reading ind_nifty200list.csv: {e}")

    # 2. Try reading from local file if user provided it (legacy name)
    if os.path.exists("nifty200.csv"):
        try:
            # Check if it's a valid CSV or the HTML error page we saw earlier
            df = pd.read_csv("nifty200.csv")
            if "Symbol" in df.columns:
                print("Found nifty200.csv with 'Symbol' column.")
                symbols = df["Symbol"].tolist()
                return symbols
            elif "SYMBOL" in df.columns:
                 print("Found nifty200.csv with 'SYMBOL' column.")
                 symbols = df["SYMBOL"].tolist()
                 return symbols
            else:
                print("nifty200.csv found but could not find 'Symbol' column. It might be invalid.")
        except Exception as e:
            print(f"Error reading nifty200.csv: {e}")

    # 3. Fallback to Nifty 50 from nselib
    print("Falling back to Nifty 50 from nselib...")
    try:
        df_nifty50 = cm.nifty50_equity_list()
        symbols = df_nifty50['Symbol'].tolist()
        print(f"Retrieved {len(symbols)} symbols from Nifty 50.")
    except Exception as e:
        print(f"Error retrieving Nifty 50 list: {e}")
        
    return symbols

def download_data(symbols):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created directory: {OUTPUT_FOLDER}")

    print(f"Downloading data for {len(symbols)} symbols...")
    
    for i, symbol in enumerate(symbols):
        # Yahoo Finance expects .NS for NSE stocks
        yf_symbol = f"{symbol}.NS"
        print(f"[{i+1}/{len(symbols)}] Downloading {yf_symbol}...")
        
        try:
            # Download data
            data = yf.download(yf_symbol, start=START_DATE, end=END_DATE, progress=False)
            
            if not data.empty:
                # Save to CSV
                file_path = os.path.join(OUTPUT_FOLDER, f"{symbol}.csv")
                data.to_csv(file_path)
                # print(f"Saved {file_path}")
            else:
                print(f"No data found for {yf_symbol}")
                
        except Exception as e:
            print(f"Failed to download {yf_symbol}: {e}")

if __name__ == "__main__":
    symbols = get_nifty_symbols()
    
    if symbols:
        # Clean symbols (remove whitespace, etc)
        symbols = [s.strip() for s in symbols]
        download_data(symbols)
        print("Download complete.")
    else:
        print("No symbols found to download.")
