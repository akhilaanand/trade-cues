import requests
import json
from datetime import datetime
import os
from financial_data import get_market_data
import pandas as pd  # Make sure pandas is imported here

def create_slack_message(sgx_data: pd.DataFrame, vix_data: pd.DataFrame, gold_data: pd.DataFrame):
    """Create a formatted Slack message with market summary"""
    if sgx_data.empty or vix_data.empty or gold_data.empty:
        return [{"type": "section", "text": {"type": "plain_text", "text": "⚠️ Could not retrieve all market data."}}]

    # Get latest data points
    sgx_latest = sgx_data.iloc[-1]
    vix_latest = vix_data.iloc[-1]
    gold_latest = gold_data.iloc[-1]

    # Ensure we're comparing scalar values
    sgx_close = sgx_latest['Close']
    vix_close = vix_latest['Close']
    gold_close = gold_latest['Close']

    # Format date
    date_str = datetime.now().strftime('%Y-%m-%d')

    # SGX data formatting
    sgx_open = sgx_latest['Open']
    sgx_emoji = ":chart_with_upwards_trend:" if sgx_close > sgx_open else ":chart_with_downwards_trend:"

    # VIX data formatting
    if pd.notna(vix_close):
        if vix_close < 17:
            vix_emoji = ":large_green_circle:"
        elif vix_close > 25:
            vix_emoji = ":red_circle:"
        else:
            vix_emoji = ":yellow_circle:"
    else:
        vix_emoji = ":question:"

    # Gold data formatting
    gold_open = gold_latest['Open']
    if pd.notna(gold_open) and pd.notna(gold_close) and gold_open != 0:
        gold_pct_change = ((gold_close - gold_open) / gold_open) * 100
        if abs(gold_pct_change) < 0.7:
            gold_emoji = ":yellow_circle:"
        elif gold_pct_change >= 0.7:
            gold_emoji = ":large_green_circle:"
        else:  # gold_pct_change <= -0.7
            gold_emoji = ":red_circle:"
    else:
        gold_emoji = ":question:"

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
                "text": f"*Gold* {gold_emoji}\nOpened at: {gold_open:.2f}\nClosed at: *{gold_close:.2f}*"
            }
        }
    ]
    return blocks
