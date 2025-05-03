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

for name, ticker in symbols.items():
    try:
        print(f"Fetching data for {name} ({ticker})")
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        time.sleep(2)  # Rate-limit friendly

        if data is None or data.shape[0] < 2:
            market_summary.append(f"⚠️ Could not retrieve enough data for *{name}*.")
            continue

        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        # Find Close column
        close_cols = [col for col in data.columns if "Close" in col]
        if not close_cols:
            market_summary.append(f"⚠️ No close price found for *{name}*.")
            continue

        close_col = close_cols[0]
        latest = data.iloc[-1]
        previous = data.iloc[-2]

        price = latest[close_col]
        prev_price = previous[close_col]
        change = ((price - prev_price) / prev_price) * 100

        # Format based on asset type
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

# Save output for Slack
with open("summary.txt", "w") as f:
    f.write("\n".join(market_summary))

print("\n".join(market_summary))
