import yfinance as yf
import pandas as pd
import time
from datetime import datetime

symbols = {
    "Nifty 50": "^NSEI",
    "VIX": "^VIX",
    "Gold": "GC=F"
}

VIX_HIGH = 20
GOLD_MOVE_THRESHOLD = 1.0  # %

market_summary = []
date_today = datetime.now().strftime("%Y-%m-%d")
market_summary.append(f"*Market Summary for {date_today}*\n" + "-"*30)

# Download all data in one batch
try:
    data = yf.download(list(symbols.values()), period="2d", interval="1d", group_by='ticker', progress=False)
except Exception as e:
    print(f"❌ Failed to download data: {e}")
    data = {}

# Loop through each symbol
for name, ticker in symbols.items():
    try:
        print(f"Processing {name} ({ticker})")
        df = data[ticker] if ticker in data else None
        time.sleep(1.5)  # minor delay

        if df is None or df.empty or len(df) < 2:
            market_summary.append(f"⚠️ Could not retrieve enough data for *{name}*.")
            continue

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        price = latest["Close"]
        prev_price = previous["Close"]
        change = ((price - prev_price) / prev_price) * 100

        if name == "VIX":
            color = "🔴" if price >= VIX_HIGH else "🟢"
            note = "High Volatility" if price >= VIX_HIGH else "Normal Volatility"
            summary = f"{color} *{name}*: {price:.2f} ({note})"

        elif name == "Gold":
            color = "🔴" if abs(change) >= GOLD_MOVE_THRESHOLD else "🟢"
            summary = f"{color} *{name}*: {price:.2f} ({change:+.2f}%)"

        else:
            arrow = "🔼" if change > 0 else "🔽"
            summary = f"{arrow} *{name}*: {price:.2f} ({change:+.2f}%)"

        market_summary.append(summary)

    except Exception as e:
        market_summary.append(f"❌ Error fetching *{name}* ({ticker}): {e}")
        continue

# Save and print
with open("summary.txt", "w") as f:
    f.write("\n".join(market_summary))

print("\n".join(market_summary))
