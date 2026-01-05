import pandas as pd
import os
import glob
from datetime import datetime, timedelta

def get_previous_quarter_end(date):
    """
    Rounds a date to the previous quarter end.
    Q1 (Jan-Mar) -> Prev Dec 31
    Q2 (Apr-Jun) -> Mar 31
    Q3 (Jul-Sep) -> Jun 30
    Q4 (Oct-Dec) -> Sep 30
    """
    if pd.isna(date):
        return pd.NaT
    
    month = date.month
    year = date.year
    
    if month in [1, 2, 3]:
        return pd.Timestamp(year - 1, 12, 31)
    elif month in [4, 5, 6]:
        return pd.Timestamp(year, 3, 31)
    elif month in [7, 8, 9]:
        return pd.Timestamp(year, 6, 30)
    elif month in [10, 11, 12]:
        return pd.Timestamp(year, 9, 30)
    else:
        return pd.NaT

def main():
    eps_dir = 'stock_eps'
    fin_dir = 'quarterly_fin'
    merged_dir = 'merged_dataset'
    output_file = 'data/merged_eps_quarterly_fin.csv'

    # Create merged directory if it doesn't exist
    if not os.path.exists(merged_dir):
        os.makedirs(merged_dir)

    if not os.path.exists('data'):
         os.makedirs('data')

    # Get list of all stock files (union of both directories)
    eps_files = glob.glob(os.path.join(eps_dir, '*.csv'))
    fin_files = glob.glob(os.path.join(fin_dir, '*.csv'))
    
    eps_symbols = {os.path.basename(f).replace('.csv', '') for f in eps_files}
    fin_symbols = {os.path.basename(f).replace('.csv', '') for f in fin_files}
    all_symbols = sorted(list(eps_symbols.union(fin_symbols)))
    
    all_data = []

    print(f"Found {len(all_symbols)} companies to process.")

    for symbol in all_symbols:
        # Load EPS data
        eps_path = os.path.join(eps_dir, f"{symbol}.csv")
        eps_df = pd.DataFrame()
        if os.path.exists(eps_path):
            try:
                eps_df = pd.read_csv(eps_path)
                # Parse Earnings Date
                # The format seems to be like '2026-02-19 05:00:00-05:00' or similar
                # We'll normalize to timezone-naive for simpler date math if needed, or keep as is but parse first
                eps_df['Earnings Date'] = pd.to_datetime(eps_df['Earnings Date'], errors='coerce')
                
                # Create a rounded date column for merging
                eps_df['Quarter End'] = eps_df['Earnings Date'].apply(get_previous_quarter_end)
            except Exception as e:
                print(f"Error reading EPS for {symbol}: {e}")

        # Load Quarterly Financial data
        fin_path = os.path.join(fin_dir, f"{symbol}.csv")
        fin_df = pd.DataFrame()
        if os.path.exists(fin_path):
            try:
                fin_df = pd.read_csv(fin_path)
                # The first column is unnamed or just contains dates like '2025-06-30'
                # Let's inspect the column names from previous `view_file` call
                # The first column had no header in the previous view, so it might come up as 'Unnamed: 0'
                # We should rename it to 'Quarter End' and parse dates
                if 'Unnamed: 0' in fin_df.columns:
                     fin_df.rename(columns={'Unnamed: 0': 'Quarter End'}, inplace=True)
                
                fin_df['Quarter End'] = pd.to_datetime(fin_df['Quarter End'], errors='coerce')
            except Exception as e:
                print(f"Error reading Financials for {symbol}: {e}")

        # Merge
        if not eps_df.empty and not fin_df.empty:
            merged_df = pd.merge(eps_df, fin_df, on='Quarter End', how='outer')
        elif not eps_df.empty:
            merged_df = eps_df
        elif not fin_df.empty:
            merged_df = fin_df
        else:
            continue
        
        # Sort by date
        if 'Quarter End' in merged_df.columns:
            merged_df.sort_values(by='Quarter End', ascending=False, inplace=True)
        
        # Add Symbol column
        merged_df.insert(0, 'Symbol', symbol)
        
        # Save individual file
        merged_df.to_csv(os.path.join(merged_dir, f"{symbol}.csv"), index=False)
        
        # Append to master list
        all_data.append(merged_df)

    # Combine all and save
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv(output_file, index=False)
        print(f"Successfully processed {len(all_symbols)} companies.")
        print(f"Combined data saved to {output_file}")
    else:
        print("No data found to merge.")

if __name__ == "__main__":
    main()
