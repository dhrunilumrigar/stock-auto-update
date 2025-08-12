import yfinance as yf
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import os
import json
import datetime

# 🛡️ Load Google Credentials securely from GitHub Secrets
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")
if not GOOGLE_CREDENTIALS:
    raise Exception("Google credentials not found in environment variables.")

credentials_dict = json.loads(GOOGLE_CREDENTIALS)
creds = Credentials.from_service_account_info(
    credentials_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
client = gspread.authorize(creds)
print(f"✅ Using service account: {creds.service_account_email}")

# 📄 Google Sheet name
SHEET_NAME = "StockAnalysisSheet"
spreadsheet = client.open(SHEET_NAME)
print(f"✅ Opened Google Sheet: {SHEET_NAME}")

# 🏢 List of stock symbols (can be NSE or BSE)
stock_symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

# 📅 Dynamic Date Range (last 30 days)
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=30)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")
print(f"📅 Fetching data from {start_date_str} to {end_date_str}")

for symbol in stock_symbols:
    print(f"\n📥 Fetching data for {symbol}...")

    # 📈 Fetch stock data
    df = yf.download(symbol, start=start_date_str, end=end_date_str, progress=False)

    if df.empty:
        print(f"⚠️ No data found for {symbol} in this date range — skipping.")
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

    print(f"📊 Data rows: {len(df)}")

    # 📄 Update or create worksheet
    try:
        worksheet = spreadsheet.worksheet(symbol)
        print(f"✏️ Updating existing worksheet: {symbol}")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=symbol, rows="1000", cols="20")
        print(f"🆕 Created new worksheet: {symbol}")

    # ✍️ Write data
    set_with_dataframe(worksheet, df)
    print(f"✅ Sheet updated for {symbol}")

print("\n🎯 All stocks processed successfully!")
