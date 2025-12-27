
import pandas as pd
from dateutil import parser
import os
from datetime import timedelta

def get_eps_data(symbol, end_date, stock_eps_path):
    """
    Get the EPS data for a given stock symbol and end_date.

    Args:
        symbol (str): The stock symbol.
        end_date (datetime): The end date.
        stock_eps_path (str): The path to the stock_eps folder.

    Returns:
        dict: A dictionary containing the EPS data for the last 4 and next 4 quarters.
    """
    eps_file = os.path.join(stock_eps_path, f"{symbol}.csv")
    if not os.path.exists(eps_file):
        return {
            'EPS_Q-4': 'N/A', 'EPS_Q-3': 'N/A', 'EPS_Q-2': 'N/A', 'EPS_Q-1': 'N/A',
            'EPS_Q+1': 'N/A', 'EPS_Q+2': 'N/A', 'EPS_Q+3': 'N/A', 'EPS_Q+4': 'N/A',
            'EPS_Surprise_Q-4': 'N/A', 'EPS_Surprise_Q-3': 'N/A', 'EPS_Surprise_Q-2': 'N/A', 'EPS_Surprise_Q-1': 'N/A',
            'EPS_Surprise_Q+1': 'N/A', 'EPS_Surprise_Q+2': 'N/A', 'EPS_Surprise_Q+3': 'N/A', 'EPS_Surprise_Q+4': 'N/A'
        }

    eps_df = pd.read_csv(eps_file)
    eps_df['Earnings Date'] = eps_df['Earnings Date'].apply(lambda x: parser.parse(x, ignoretz=True))
    
    # Convert dates to quarters for comparison
    end_quarter = pd.Timestamp(end_date).to_period('Q')
    eps_df['Quarter'] = eps_df['Earnings Date'].dt.to_period('Q')

    # Separate past and future earnings based on Quarter
    past_earnings = eps_df[eps_df['Quarter'] <= end_quarter].sort_values(by='Earnings Date', ascending=False)
    future_earnings = eps_df[eps_df['Quarter'] > end_quarter].sort_values(by='Earnings Date')

    # Get last 4 quarters
    last_4_quarters = past_earnings.head(4)

    # Get next 4 quarters
    next_4_quarters = future_earnings.head(4)

    eps_data = {}

    for i in range(4):
        if i < len(last_4_quarters):
            eps_data[f'EPS_Q-{i+1}'] = last_4_quarters.iloc[i]['Reported EPS']
            eps_data[f'EPS_Surprise_Q-{i+1}'] = last_4_quarters.iloc[i]['Surprise(%)']
        else:
            eps_data[f'EPS_Q-{i+1}'] = 'N/A'
            eps_data[f'EPS_Surprise_Q-{i+1}'] = 'N/A'

    for i in range(4):
        if i < len(next_4_quarters):
            eps_data[f'EPS_Q+{i+1}'] = next_4_quarters.iloc[i]['Reported EPS']
            eps_data[f'EPS_Surprise_Q+{i+1}'] = next_4_quarters.iloc[i]['Surprise(%)']
        else:
            eps_data[f'EPS_Q+{i+1}'] = 'N/A'
            eps_data[f'EPS_Surprise_Q+{i+1}'] = 'N/A'

    return eps_data

def main():
    main_df_path = '/Users/avinashladdha/___PERSONAL/Finance/stock_data/equity_analysis/analysis_results_final.csv'
    stock_eps_path = '/Users/avinashladdha/___PERSONAL/Finance/stock_data/equity_analysis/stock_eps/'
    
    main_df = pd.read_csv(main_df_path)
    main_df['End_Date'] = pd.to_datetime(main_df['End_Date'])

    # Create new columns
    new_columns = [
        'EPS_Q-4', 'EPS_Q-3', 'EPS_Q-2', 'EPS_Q-1',
        'EPS_Q+1', 'EPS_Q+2', 'EPS_Q+3', 'EPS_Q+4',
        'EPS_Surprise_Q-4', 'EPS_Surprise_Q-3', 'EPS_Surprise_Q-2', 'EPS_Surprise_Q-1',
        'EPS_Surprise_Q+1', 'EPS_Surprise_Q+2', 'EPS_Surprise_Q+3', 'EPS_Surprise_Q+4'
    ]
    for col in new_columns:
        main_df[col] = 'N/A'

    for index, row in main_df.iterrows():
        symbol = row['Symbol']
        end_date = row['End_Date']
        eps_data = get_eps_data(symbol, end_date, stock_eps_path)
        for key, value in eps_data.items():
            main_df.loc[index, key] = value
            
    output_path = '/Users/avinashladdha/___PERSONAL/Finance/stock_data/equity_analysis/analysis_results_with_eps.csv'
    main_df.to_csv(output_path, index=False)
    print(f"Processing complete. Output saved to {output_path}")

if __name__ == "__main__":
    main()
