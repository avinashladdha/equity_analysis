import pandas as pd
import yfinance as yf
import os

def get_stock_data():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(base_dir, 'ind_nifty200list.csv')
    output_csv = os.path.join(base_dir, 'nifty200_data.csv')

    # Read input CSV
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: {input_csv} not found.")
        return

    results = []

    print(f"Fetching data for {len(df)} companies...")

    for index, row in df.iterrows():
        symbol = row['Symbol']
        company_name = row['Company Name']
        ns_symbol = f"{symbol}.NS"
        
        print(f"Processing {index + 1}/{len(df)}: {company_name} ({ns_symbol})")

        try:
            ticker = yf.Ticker(ns_symbol)
            info = ticker.info
            
            # 1. Market Cap
            market_cap = info.get('marketCap', None)

            # 2. Earnings data in last 5 years
            # We'll use 'Net Income' from financials as a proxy for earnings data if EPS isn't directly structured as a time series in a simple way
            # Alternatively, ticker.earnings_history might be available but ticker.financials is more robust for yearly data.
            # Let's try to get Net Income from financials (annual)
            
            financials = ticker.financials
            earnings_data = {}
            
            if not financials.empty:
                # 'Net Income' is usually a row label. 
                # Note: yfinance structure can vary. usually 'Net Income' or 'Net Income Common Stockholders'
                
                # Let's try to find a row that looks like Net Income
                net_income_row = None
                if 'Net Income' in financials.index:
                    net_income_row = financials.loc['Net Income']
                elif 'Net Income Common Stockholders' in financials.index:
                    net_income_row = financials.loc['Net Income Common Stockholders']
                
                if net_income_row is not None:
                    # Get last 5 years (columns are dates)
                    # Sort columns just in case
                    sorted_dates = sorted(financials.columns, reverse=True)
                    
                    # We want up to 5 years
                    years_to_fetch = sorted_dates[:5]
                    
                    for i, date in enumerate(years_to_fetch):
                         # Format date as YYYY-MM-DD or just Year
                        year_str = date.strftime('%Y')
                        earnings_data[f'Earnings_{year_str}'] = net_income_row[date]
                else:
                    print(f"  Warning: 'Net Income' not found for {symbol}")

            # Assemble record
            record = {
                'Company Name': company_name,
                'Symbol': symbol,
                'Market Cap': market_cap,
            }
            record.update(earnings_data)
            results.append(record)

        except Exception as e:
            print(f"  Error fetching data for {symbol}: {e}")

    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Save to CSV
    results_df.to_csv(output_csv, index=False)
    print(f"Data saved to {output_csv}")

if __name__ == "__main__":
    get_stock_data()
