import yfinance as yf
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Style
import pandas as pd

# Initialize colorama
colorama.init(autoreset=True)

def get_market_data():
    """
    Fetch market data for SGX Nifty, VIX, and Gold
    """
    # Define ticker symbols
    sgx_ticker = "^NSEI"  # Using NSE index since SGX Nifty futures aren't directly available
    vix_ticker = "^VIX"
    gold_ticker = "GC=F"  # Gold Futures
    
    # Get end date (today) and start date (yesterday)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)  # Get 2 days to ensure we have yesterday's data
    
    # Format dates
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    # Fetch data
    sgx_data = yf.download(sgx_ticker, start=start_date_str, end=end_date_str)
    vix_data = yf.download(vix_ticker, start=start_date_str, end=end_date_str)
    gold_data = yf.download(gold_ticker, start=start_date_str, end=end_date_str)
    
    return sgx_data, vix_data, gold_data

def format_sgx(data):
    """Format SGX data with color coding"""
    # Get the most recent complete trading day
    latest_data = data.iloc[-1]
    
    open_price = latest_data['Open']
    close_price = latest_data['Close']
    
    # Color code based on performance
    if close_price > open_price:
        close_display = f"{Fore.GREEN}{close_price:.2f}{Style.RESET_ALL}"
    else:
        close_display = f"{Fore.RED}{close_price:.2f}{Style.RESET_ALL}"
    
    return f"SGX - opened at {open_price:.2f}, closed at {close_display}"

def format_vix(data):
    """Format VIX data with color coding based on volatility levels"""
    # Get the most recent complete trading day
    latest_data = data.iloc[-1]
    close_price = latest_data['Close']
    
    # Color code based on VIX level
    if close_price < 17:
        vix_display = f"{Fore.LIGHTGREEN_EX}{close_price:.2f}{Style.RESET_ALL}"
    elif close_price > 25:
        vix_display = f"{Fore.RED}{close_price:.2f}{Style.RESET_ALL}"
    else:
        vix_display = f"{Fore.YELLOW}{close_price:.2f}{Style.RESET_ALL}"
    
    return f"VIX - current level: {vix_display}"

def format_gold(data):
    """Format Gold data with color coding based on daily change percentage"""
    # Get the most recent complete trading day
    latest_data = data.iloc[-1]
    
    open_price = latest_data['Open']
    close_price = latest_data['Close']
    
    # Calculate percentage change
    percent_change = ((close_price - open_price) / open_price) * 100
    
    # Color code based on price change
    if abs(percent_change) < 0.7:
        change_display = f"{Fore.YELLOW}{percent_change:.2f}%{Style.RESET_ALL}"
    elif percent_change >= 0.7:
        change_display = f"{Fore.GREEN}{percent_change:.2f}%{Style.RESET_ALL}"
    else:  # percent_change <= -0.7
        change_display = f"{Fore.RED}{percent_change:.2f}%{Style.RESET_ALL}"
    
    return f"Gold - price: ${close_price:.2f}, daily change: {change_display}"

def generate_summary():
    """Generate and display the formatted market summary"""
    print(f"\nMarket Summary for {datetime.now().strftime('%Y-%m-%d')}")
    print("-" * 50)
    
    try:
        sgx_data, vix_data, gold_data = get_market_data()
        
        # Format and print each data point
        print(format_sgx(sgx_data))
        print(format_vix(vix_data))
        print(format_gold(gold_data))
        
        # Return the data for potential email sending
        return {
            "sgx": sgx_data.iloc[-1].to_dict(),
            "vix": vix_data.iloc[-1].to_dict(),
            "gold": gold_data.iloc[-1].to_dict(),
            "date": datetime.now().strftime('%Y-%m-%d')
        }
        
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

if __name__ == "__main__":
    generate_summary()
