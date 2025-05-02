import yfinance as yf
import time
from datetime import datetime

# Define the symbols to track
symbols = {
    "Nifty 50": "^NSEI",
    "VIX": "^VIX",
    "Gold": "GC=F"
}

# Define thresholds
VIX_HIGH = 20
GOLD_MOVE_THRESHOLD = 1.0  # % change considered significant

market_summary = []
date_today = datetime.now().strftime("%Y-%m-%d")
market_summary.append(f"*Market Summary for {date_today}*\n" + "-"*30)

for name, ticker in symbols.items():
    try:
        print(f"Fetching data for {name} ({ticker})")
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        time.sleep(3)  # To avoid rate limiting

        if data.empty or len(data) < 2:
            market_summary.append(f"⚠️ Could not retrieve enough data for *{name}*.")
            continue

        latest = data.iloc[-1]
        previous = data.iloc[-2]

        price = latest['Close']
        change = ((latest['Close'] - previous['Close']) / previous['Close']) * 100

        # Color code based on logic
        if name == "VIX":
            if price >= VIX_HIGH:
                color = "🔴"
                note = "High Volatility"
            else:
                color = "🟢"
                note = "Normal Volatility"
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

# Save summary to file for Slack script
with open("summary.txt", "w") as f:
    f.write("\n".join(market_summary))

print("\n".join(market_summary))
