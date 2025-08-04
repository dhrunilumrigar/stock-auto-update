# stock-auto-update
# 📈 Auto-Updating Stock Market Google Sheet using GitHub Actions

This project automatically fetches real-time stock market data (e.g., from NSE: RELIANCE.NS, TCS.NS) and updates a Google Sheet every 10 minutes during market hours. It uses **GitHub Actions**, **Yahoo Finance API**, and **Google Sheets API**.

---

## 🚀 Features

- ✅ Pulls latest stock data using `yfinance`
- ✅ Calculates key indicators:
  - EMA20, EMA50
  - RSI (14)
  - Daily % change
- ✅ Writes data to separate worksheets for each company
- ✅ Runs every 10 minutes during NSE market hours using GitHub Actions
- ✅ Stores Google Sheets credentials securely via GitHub Secrets

---

## 🔧 Tech Stack

- Python 3.11
- [yfinance](https://pypi.org/project/yfinance/)
- [gspread](https://pypi.org/project/gspread/)
- Google Sheets API
- GitHub Actions (CI/CD)

---

## 📁 File Structure

