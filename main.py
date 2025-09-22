import yfinance as yf
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import os
import json
from datetime import datetime, timedelta

# Load Google credentials from GitHub Secrets
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")
if not GOOGLE_CREDENTIALS:
    raise ValueError("Missing GOOGLE_CREDENTIALS in environment variables")
creds_dict = json.loads(GOOGLE_CREDENTIALS)

# Authenticate with Google Sheets
creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)

# Load Spreadsheet URL from GitHub Secrets
SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL")
if not SPREADSHEET_URL:
    raise ValueError("Missing SPREADSHEET_URL in environment variables")

# Open the spreadsheet and specific worksheet
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.worksheet("StockAnalysisSheet")  # Your sheet name

# Stock symbols (simple hardcoded list)
symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

# Date range (last 7 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Fetch stock data
all_data = []
for symbol in symbols:
    if not symbol:
        continue
    
    df = yf.download(symbol, start=start_date, end=end_date, interval="1m")

    # ADDED CHECK: Skip to the next symbol if no data is returned
    if df.empty:
        print(f"Warning: No data downloaded for {symbol}. Skipping.")
        continue

    df = df.reset_index()

    # Convert timestamp to IST
    df["Datetime"] = pd.to_datetime(df["Datetime"]).dt.tz_convert('Asia/Kolkata')
    df["Symbol"] = symbol
    all_data.append(df)

# Check if any data was fetched
if not all_data:
    print("No data fetched for any symbols. Exiting.")
else:
    # Merge all stock data
    final_df = pd.concat(all_data)

    # Reorder columns
    final_df = final_df[["Symbol", "Datetime", "Open", "High", "Low", "Close", "Volume"]]

    # Format datetime with seconds
    final_df["Datetime"] = final_df["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Upload to Google Sheets
    worksheet.clear()
    set_with_dataframe(worksheet, final_df)

    print(f"✅ Stock data updated for symbols: {final_df['Symbol'].unique().tolist()}")
