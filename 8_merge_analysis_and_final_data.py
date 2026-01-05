import pandas as pd
import os

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

def process_financial_data(fin_df):
    """
    Adds lag and lead metrics for specified columns.
    """
    # Ensure sorted by Symbol and Date for shifting
    fin_df = fin_df.sort_values(by=['Symbol', 'Quarter End'], ascending=[True, True]).copy()
    
    metrics = ['Total Revenue', 'Gross Profit', 'Diluted EPS', 'EBITDA']
    
    # Verify metrics exist
    existing_metrics = [m for m in metrics if m in fin_df.columns]
    if len(existing_metrics) != len(metrics):
        missing = set(metrics) - set(existing_metrics)
        print(f"Warning: Missing columns in financial data: {missing}")
    
    for metric in existing_metrics:
        # q (current)
        fin_df[f'{metric}_q'] = fin_df[metric]
        
        # q-1 (previous quarter)
        fin_df[f'{metric}_q-1'] = fin_df.groupby('Symbol')[metric].shift(1)
        
        # q-2 (2 quarters ago)
        fin_df[f'{metric}_q-2'] = fin_df.groupby('Symbol')[metric].shift(2)
        
        # q+1 (next quarter)
        fin_df[f'{metric}_q+1'] = fin_df.groupby('Symbol')[metric].shift(-1)
        
        # q+2 (2 quarters ahead)
        fin_df[f'{metric}_q+2'] = fin_df.groupby('Symbol')[metric].shift(-2)
        
    return fin_df

def main():
    analysis_file = 'data/analysis_results_final.csv'
    financial_file = 'data/merged_eps_quarterly_fin.csv'
    output_file = 'data/final.csv'

    if not os.path.exists(analysis_file):
        print(f"Error: {analysis_file} not found.")
        return
    
    if not os.path.exists(financial_file):
        print(f"Error: {financial_file} not found.")
        return

    print("Loading analysis data...")
    analysis_df = pd.read_csv(analysis_file)
    print(f"Analysis records: {len(analysis_df)}")

    # Parse Start_Date
    analysis_df['Start_Date'] = pd.to_datetime(analysis_df['Start_Date'], errors='coerce')
    
    # Create Quarter End column for merging
    print("calculating quarter ends...")
    analysis_df['Quarter End'] = analysis_df['Start_Date'].apply(get_previous_quarter_end)

    print("Loading financial data...")
    fin_df = pd.read_csv(financial_file)
    print(f"Financial records: {len(fin_df)}")
    
    # Ensure Quarter End is datetime in financial data
    fin_df['Quarter End'] = pd.to_datetime(fin_df['Quarter End'], errors='coerce')

    # Process financial data to add lags/leads
    print("Processing financial data (adding lags/leads)...")
    fin_df = process_financial_data(fin_df)

    print("Merging data...")
    # Left join to keep all analysis records and attach matching financials
    merged_df = pd.merge(analysis_df, fin_df, on=['Symbol', 'Quarter End'], how='left')
    
    print(f"Merged records: {len(merged_df)}")
    
    # Save output
    merged_df.to_csv(output_file, index=False)
    print(f"Saved merged data to {output_file}")

if __name__ == "__main__":
    main()
