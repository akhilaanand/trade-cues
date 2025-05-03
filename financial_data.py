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
        print(f"\nFetching data for {name} ({ticker})")
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        time.sleep(2)

        if data is None or not isinstance(data, pd.DataFrame):
            market_summary.append(f"⚠️ No DataFrame returned for *{name}*.")
            continue

        if data.empty:
            market_summary.append(f"⚠️ Empty data for *{name}*.")
            continue

        if len(data) < 2:
            market_summary.append(f"⚠️ Not enough rows in data for *{name}*.")
            continue

        # Flatten columns if MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        # Try to find a close column
        close_col = None
        possible_close_cols = [col for col in data.columns if "close" in col.lower()]
        if "Close" in data.columns:
            close_col = "Close"
        elif possible_close_cols:
            close_col = possible_close_cols[0]
        else:
            market_summary.append(f"⚠️ No 'Close' or similar column found for *{name}*. Columns: {list(data.columns)}")
            continue

        try:
            latest = data.iloc[-1]
            previous = data.iloc[-2]

            price = float(latest[close_col])
            prev_price = float(previous[close_col])
        except Exception as e:
            market_summary.append(f"⚠️ Could not extract price values for *{name}*: {e}")
            continue

        if prev_price == 0:
            market_summary.append(f"⚠️ Previous price is zero for *{name}*, cannot compute change.")
            continue

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

# Save to file and print
output = "\n".join(market_summary)
with open("summary.txt", "w") as f:
    f.write(output)

print(output)
