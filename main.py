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
creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)

# Load Spreadsheet URL
SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL")
if not SPREADSHEET_URL:
    raise ValueError("Missing SPREADSHEET_URL in environment variables")

spreadsheet = gc.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.worksheet("StockAnalysisSheet")

# Stock symbols
symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

# Date range (last 5 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=5)

# Download data
data = yf.download(symbols, start=start_date, end=end_date, interval="5m", group_by="ticker")

# Prepare clean DataFrame
final_df = pd.DataFrame()

for symbol in symbols:
    if symbol in data:
        temp = data[symbol].copy()
        temp["Datetime"] = temp.index
        temp["Symbol"] = symbol
        temp.reset_index(drop=True, inplace=True)

        # Ensure Close is numeric
        temp["Close"] = pd.to_numeric(temp["Close"], errors="coerce")
        temp.dropna(subset=["Close"], inplace=True)

        final_df = pd.concat([final_df, temp], ignore_index=True)

# --- FIX: Handle timezone properly ---
if pd.api.types.is_datetime64tz_dtype(final_df["Datetime"]):
    final_df["Datetime"] = final_df["Datetime"].dt.tz_convert("Asia/Kolkata")
else:
    final_df["Datetime"] = pd.to_datetime(final_df["Datetime"]).dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata")

# Format timestamp for Google Sheets
final_df["Datetime"] = final_df["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Select and reorder columns
final_df = final_df[["Datetime", "Symbol", "Open", "High", "Low", "Close", "Volume"]]

# Upload to Google Sheets
worksheet.clear()
set_with_dataframe(worksheet, final_df)

print("✅ Google Sheet updated with correct timestamps and Close values.")
