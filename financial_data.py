import yfinance as yf
import time
from datetime import date, datetime
import pandas as pd

def get_market_data():
    """
    Fetch market data for financial indices
    Returns the data frames for each index
    """
    symbols = {
        "NIFTY 50": "^NSEI",
        "SGX Nifty": "^STI",  # Using STI as a proxy, actual SGX might need a different ticker or source
        "INDIA VIX": "^INDIAVIX",  # Using correct VIX ticker
        "GOLD": "GC=F",
        "USD/INR": "INR=X"
    }
    
    data_frames = {}
    
    for name, ticker in symbols.items():
        try:
            print(f"Fetching data for {name} ({ticker})")
            data = yf.download(ticker, period="2d", interval="1d", progress=False)
            time.sleep(1)  # Reduced sleep time
            
            if data is None or data.empty:
                print(f"⚠️ No data for {name}.")
                continue
                
            data_frames[name] = data
            
        except Exception as e:
            print(f"❌ Error fetching {name} ({ticker}): {e}")
            
    return data_frames

def generate_summary():
    """Generate and display the formatted market summary"""
    market_summary = [f"Market Summary for {date.today().strftime('%Y-%m-%d')}\n",
                      "--------------------------------------------------"]
    
    try:
        data_frames = get_market_data()
        
        for name, data in data_frames.items():
            if len(data) < 2:
                market_summary.append(f"⚠️ Insufficient data points for {name}.")
                continue
                
            latest = data.iloc[-1]
            previous = data.iloc[-2]
            
            # Safely extract the Close price
            try:
                latest_price = float(latest["Close"])
                previous_price = float(previous["Close"])
            except KeyError:
                # If 'Close' isn't available, try to find an alternative
                close_cols = [col for col in data.columns if "close" in str(col).lower()]
                if close_cols:
                    latest_price = float(latest[close_cols[0]])
                    previous_price = float(previous[close_cols[0]])
                else:
                    market_summary.append(f"⚠️ No 'Close' column found for {name}.")
                    continue
            
            if previous_price == 0:
                market_summary.append(f"⚠️ Previous price is zero for {name}, cannot compute change.")
                continue
                
            change = ((latest_price - previous_price) / previous_price) * 100
            
            # Format the output based on the symbol
            if name == "INDIA VIX":
                if float(change) > 5:
                    market_summary.append(f"⚠️ {name} is up by {change:.2f}%. Market volatility might be increasing.")
                elif float(change) < -5:
                    market_summary.append(f"✅ {name} is down by {change:.2f}%. Market volatility might be decreasing.")
                else:
                    market_summary.append(f"{name} change: {change:.2f}%.")
            elif name == "GOLD":
                if float(change) > 1:
                    market_summary.append(f"⬆️ {name} is up by {change:.2f}%.")
                elif float(change) < -1:
                    market_summary.append(f"⬇️ {name} is down by {change:.2f}%.")
                else:
                    market_summary.append(f"{name} change: {change:.2f}%.")
            elif name == "USD/INR":
                if float(change) > 0.5:
                    market_summary.append(f"⬆️ {name} is up by {change:.2f}%.")
                elif float(change) < -0.5:
                    market_summary.append(f"⬇️ {name} is down by {change:.2f}%.")
                else:
                    market_summary.append(f"{name} change: {change:.2f}%.")
            else:
                market_summary.append(f"{name} change: {change:.2f}%.")
                
    except Exception as e:
        market_summary.append(f"❌ Error generating market summary: {str(e)}")
    
    # Print the summary
    full_summary = "\n".join(market_summary)
    print(full_summary)
    
    return market_summary

if __name__ == "__main__":
    generate_summary()
