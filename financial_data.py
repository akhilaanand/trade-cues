import yfinance as yf
import time
from datetime import date

symbols = {
    "NIFTY 50": "^NSEI",
    "SGX Nifty": "^STI",  # Using STI as a proxy, actual SGX might need a different ticker or source
    "INDIA VIX": "^NSEI",  # VIX ticker might need verification
    "GOLD": "GC=F",
    "USD/INR": "INR=X"
}

market_summary = [f"Market Summary for {date.today().strftime('%Y-%m-%d')}\n",
                  "--------------------------------------------------"]

print("YF.download() has changed argument auto_adjust default to True\n")

for name, ticker in symbols.items():
    try:
        print(f"\nFetching data for {name} ({ticker})")
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        time.sleep(2)

        # Check if data is valid
        if data is None or data.empty:
            market_summary.append(f"⚠️ No data for {name}.")
            continue

        print(f"Columns for {name}: {list(data.columns)}")
        close_col = None
        possible_close_cols = [col for col in data.columns if "close" in col.lower()]

        print(f"Possible Close columns for {name}: {possible_close_cols}")

        if "Close" in data.columns:
            close_col = "Close"
        elif possible_close_cols:
            close_col = possible_close_cols[0]
        else:
            market_summary.append(f"⚠️ No 'Close' or similar column found for {name}.")
            continue

        # Get the latest and previous data
        if len(data) < 2:
            market_summary.append(f"⚠️ Insufficient data points (less than 2 days) for {name}.")
            continue

        latest = data.iloc[-1]
        previous = data.iloc[-2]

        if not isinstance(latest, pd.Series) or not isinstance(previous, pd.Series):
            market_summary.append(f"⚠️ Error: Could not retrieve latest or previous price for {name} as Series.")
            continue

        if close_col not in latest or close_col not in previous:
            market_summary.append(f"⚠️ No valid price data in latest or previous for {name}. Check the data columns.")
            continue

        price = float(latest[close_col])
        prev_price = float(previous[close_col])

        if prev_price == 0:
            market_summary.append(f"⚠️ Previous price is zero for {name}, cannot compute change.")
            continue

        change = ((price - prev_price) / prev_price) * 100

        if name == "INDIA VIX":
            if change > 5:
                market_summary.append(f"⚠️ {name} is up by {change:.2f}%. Market volatility might be increasing.")
            elif change < -5:
                market_summary.append(f"✅ {name} is down by {change:.2f}%. Market volatility might be decreasing.")
            else:
                market_summary.append(f"{name} change: {change:.2f}%.")
        elif name == "GOLD":
            if change > 1:
                market_summary.append(f"⬆️ {name} is up by {change:.2f}%.")
            elif change < -1:
                market_summary.append(f"⬇️ {name} is down by {change:.2f}%.")
            else:
                market_summary.append(f"{name} change: {change:.2f}%.")
        elif name == "USD/INR":
            if change > 0.5:
                market_summary.append(f"⬆️ {name} is up by {change:.2f}%.")
            elif change < -0.5:
                market_summary.append(f"⬇️ {name} is down by {change:.2f}%.")
            else:
                market_summary.append(f"{name} change: {change:.2f}%.")
        else:
            market_summary.append(f"{name} ({ticker}) change: {change:.2f}%.")

    except Exception as e:
        market_summary.append(f"❌ Error fetching *{name}* ({ticker}): {e}")
        continue

print("\n".join(market_summary))
