import requests
import json
import os
from datetime import datetime
from financial_data_fixed import get_market_data

def send_slack_message():
    """Send market summary to Slack"""
    try:
        # Get Slack webhook URL from environment variable
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        
        if not webhook_url:
            print("Error: SLACK_WEBHOOK_URL environment variable not set")
            return False
        
        # Generate market summary
        data_frames = get_market_data()
        
        # Create blocks for message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Market Summary for {datetime.now().strftime('%Y-%m-%d')}",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for name, data in data_frames.items():
            if len(data) < 2:
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
                    continue
            
            if previous_price == 0:
                continue
                
            change = ((latest_price - previous_price) / previous_price) * 100
            
            # Format the message with emoji based on the symbol and change
            emoji = "🔄"
            if name == "INDIA VIX":
                if change > 5:
                    emoji = "⚠️"
                    description = "Market volatility might be increasing."
                elif change < -5:
                    emoji = "✅"
                    description = "Market volatility might be decreasing."
                else:
                    description = ""
            elif name == "GOLD":
                if change > 1:
                    emoji = "⬆️"
                    description = "Significant rise."
                elif change < -1:
                    emoji = "⬇️"
                    description = "Significant fall."
                else:
                    description = ""
            elif name == "USD/INR":
                if change > 0.5:
                    emoji = "⬆️"
                    description = "Rupee weakening."
                elif change < -0.5:
                    emoji = "⬇️"
                    description = "Rupee strengthening."
                else:
                    description = ""
            else:
                if change > 1:
                    emoji = "⬆️"
                    description = ""
                elif change < -1:
                    emoji = "⬇️"
                    description = ""
                else:
                    description = ""
            
            # Add section for this market data
            block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{name}* {emoji}\nCurrent: *{latest_price:.2f}*\nChange: *{change:.2f}%*"
                }
            }
            
            if description:
                block["text"]["text"] += f"\n_{description}_"
                
            blocks.append(block)
        
        # Add time of generation
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": f"Generated at {datetime.now().strftime('%H:%M:%S')} UTC",
                    "emoji": True
                }
            ]
        })
        
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
