import yfinance as yf
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import os
import json
from datetime import datetime, timedelta

# Load Google credentials
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")
if not GOOGLE_CREDENTIALS:
    raise ValueError("Missing GOOGLE_CREDENTIALS in environment variables")
creds_dict = json.loads(GOOGLE_CREDENTIALS)

# Authenticate with Google Sheets
creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)

# Your Google Sheet URL
SPREADSHEET_URL = "YOUR_GOOGLE_SHEET_URL_HERE"

# Open the sheet
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.sheet1

# Stock symbols
symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

# Date range (last 7 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Fetch data
all_data = []
for symbol in symbols:
    df = yf.download(symbol, start=start_date, end=end_date, interval="1m")  # 1-minute interval
    df = df.reset_index()

    # Convert timestamp to local IST time
    df["Datetime"] = pd.to_datetime(df["Datetime"]).dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')

    df["Symbol"] = symbol
    all_data.append(df)

# Merge all data
final_df = pd.concat(all_data)

# Reorder columns
final_df = final_df[["Symbol", "Datetime", "Open", "High", "Low", "Close", "Volume"]]

# Ensure datetime format with seconds
final_df["Datetime"] = final_df["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Upload to Google Sheets
worksheet.clear()
set_with_dataframe(worksheet, final_df)

print("✅ Stock data updated with exact timestamps!")
