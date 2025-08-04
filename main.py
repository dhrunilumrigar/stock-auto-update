import yfinance as yf
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import os
import json

# 🛡️ Load Google Credentials securely from GitHub Secrets
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")
if not GOOGLE_CREDENTIALS:
    raise Exception("Google credentials not found in environment variables.")
credentials_dict = json.loads(GOOGLE_CREDENTIALS)
creds = Credentials.from_service_account_info(credentials_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(creds)

# 📄 Google Sheet name
SHEET_NAME = "StockAnalysisSheet"
spreadsheet = client.open(SHEET_NAME)

# 🏢 List of stock symbols (can be NSE or BSE)
stock_symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

# 📅 Date Range
start_date = "2024-07-01"
end_date = "2024-07-31"

for symbol in stock_symbols:
    print(f"📥 Fetching data for {symbol}...")

    # 📈 Fetch stock data
    df = yf.download(symbol, start=start_date, end=end_date, progress=False)

    if df.empty:
        print(f"⚠️ No data for {symbol}")
        continue

    df.reset_index(inplace=True)

    # 📊 Indicators
    df["Daily % Change (%)"] = df["Close"].pct_change() * 100
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI_14"] = 100 - (100 / (1 + rs))

    # 📄 Update or create worksheet
    try:
        worksheet = spreadsheet.worksheet(symbol)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=symbol, rows="1000", cols="20")

    # ✍️ Write data
    set_with_dataframe(worksheet, df)
    print(f"✅ Updated Google Sheet for {symbol}")

