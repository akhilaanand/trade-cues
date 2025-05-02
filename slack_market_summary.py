import requests
import json
from datetime import datetime
import os
from financial_data import get_market_data

def create_slack_message(sgx_data, vix_data, gold_data):
    """Create a formatted Slack message with market summary"""
    # Get latest data points
    sgx_latest = sgx_data.iloc[-1]
    vix_latest = vix_data.iloc[-1]
    gold_latest = gold_data.iloc[-1]
    
    # Format date
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # SGX data formatting
    sgx_open = sgx_latest['Open']
    sgx_close = sgx_latest['Close']
    sgx_emoji = ":chart_with_upwards_trend:" if sgx_close > sgx_open else ":chart_with_downwards_trend:"
    
    # VIX data formatting
    vix_close = vix_latest['Close']
    if vix_close < 17:
        vix_emoji = ":large_green_circle:"
    elif vix_close > 25:
        vix_emoji = ":red_circle:"
    else:
        vix_emoji = ":yellow_circle:"
    
    # Gold data formatting
    gold_open = gold_latest['Open']
    gold_close = gold_latest['Close']
    gold_pct_change = ((gold_close - gold_open) / gold_open) * 100
    
    if abs(gold_pct_change) < 0.7:
        gold_emoji = ":yellow_circle:"
    elif gold_pct_change >= 0.7:
        gold_emoji = ":large_green_circle:"
    else:  # gold_pct_change <= -0.7
        gold_emoji = ":red_circle:"
    
    # Create blocks for Slack message (modern formatting)
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Market Summary for {date_str}",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*SGX* {sgx_emoji}\nOpened at: {sgx_open:.2f}\nClosed at: *{sgx_close:.2f}*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*VIX* {vix_emoji}\nCurrent level: *{vix_close:.2f}*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Gold* {gold_emoji}\nPrice: *${gold_close:.2f}*\nDaily change: *{gold_pct_change:.2f}%*"
            }
        }
    ]
    
    return blocks

def send_slack_message():
    """Send market summary to Slack"""
    try:
        # Get Slack webhook URL from environment variable
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        
        if not webhook_url:
            print("Error: SLACK_WEBHOOK_URL environment variable not set")
            return False
            
        # Get market data
        sgx_data, vix_data, gold_data = get_market_data()
        
        # Create message blocks
        blocks = create_slack_message(sgx_data, vix_data, gold_data)
        
        # Prepare payload
        payload = {
            "blocks": blocks,
            "text": f"Market Summary for {datetime.now().strftime('%Y-%m-%d')}"  # Fallback text
        }
        
        # Send to Slack
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("Message sent to Slack successfully")
            return True
        else:
            print(f"Failed to send message to Slack. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending Slack message: {e}")
        return False

if __name__ == "__main__":
    send_slack_message()
