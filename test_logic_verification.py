import yfinance as yf
import pandas as pd
import numpy as np

symbol = "RELIANCE"
ns_symbol = f"{symbol}.NS"

print(f"Testing logic for {ns_symbol}...")

try:
    ticker = yf.Ticker(ns_symbol)
    q_financials = ticker.quarterly_financials
    
    if q_financials is not None and not q_financials.empty:
        print("Fetched Quarterly Financials.")
        
        hist = ticker.history(period="5y")
        print(f"Fetched History: {len(hist)} rows.")
        
        if not hist.empty and 'Basic Average Shares' in q_financials.index:
            market_caps = []
            print("\nCalculating Market Caps:")
            for date in q_financials.columns:
                ts = pd.to_datetime(date)
                
                # Logic from the script
                ts_naive = ts.tz_localize(None)
                if hist.index.tz is not None:
                     hist_index_naive = hist.index.tz_localize(None)
                else:
                     hist_index_naive = hist.index
                
                mask = hist_index_naive <= ts_naive
                valid_hist = hist[mask]
                
                if not valid_hist.empty:
                    price = valid_hist.iloc[-1]['Close']
                    shares = q_financials.loc['Basic Average Shares', date]
                    mcap = price * shares
                    print(f"Date: {date} (Naive: {ts_naive}) -> Price Date: {valid_hist.index[-1]} -> Price: {price} -> Shares: {shares} -> Mcap: {mcap}")
                    market_caps.append(mcap)
                else:
                    print(f"Date: {date} -> No valid history found.")
                    market_caps.append(None)
            
            q_financials.loc['Market Cap'] = market_caps
            print("\nResulting DataFrame (Tail):")
            print(q_financials.tail(3))
        else:
            print("Missing Basic Average Shares or History empty.")

except Exception as e:
    print(f"Error: {e}")
