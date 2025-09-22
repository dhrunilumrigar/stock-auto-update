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

# --- MODIFICATION: Download all stocks at once ---
# yfinance will return a wide DataFrame with multi-level columns
data = yf.download(symbols, start=start_date, end=end_date, interval="1m")

# Check if any data was fetched
if data.empty:
    print("No data fetched for the given symbols. Exiting.")
else:
    # --- MODIFICATION: Flatten the multi-level column headers ---
    # The original headers are like ('Open', 'RELIANCE.NS'). We want 'Open: RELIANCE.NS'
    data.columns = [f"{level[0]}: {level[1]}" for level in data.columns]
    
    # Move the 'Datetime' index into a regular column
    data.reset_index(inplace=True)

    # Convert timestamp to IST and format it
    data['Datetime'] = pd.to_datetime(data['Datetime']).dt.tz_convert('Asia/Kolkata')
    data['Datetime'] = data['Datetime'].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Upload the new wide dataframe to Google Sheets
    worksheet.clear()
    set_with_dataframe(worksheet, data)

    print(f"✅ Stock data updated in wide format for symbols: {symbols}")
