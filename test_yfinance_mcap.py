import yfinance as yf
import pandas as pd

try:
    ticker = yf.Ticker("RELIANCE.NS")
    print("--- Quarterly Financials ---")
    qf = ticker.quarterly_financials
    print(qf.index)
    print(qf.columns)
    
    print("\n--- Quarterly Balance Sheet ---")
    qbs = ticker.quarterly_balance_sheet
    if qbs is not None:
        print(qbs.index)
        if 'Ordinary Shares Number' in qbs.index:
            print("Found Ordinary Shares Number")
            print(qbs.loc['Ordinary Shares Number'])
        if 'Share Issued' in qbs.index:
            print("Found Share Issued")
            
    print("\n--- Info ---")
    info = ticker.info
    print(f"Market Cap: {info.get('marketCap')}")
    print(f"Shares Outstanding: {info.get('sharesOutstanding')}")

except Exception as e:
    print(f"Error: {e}")
