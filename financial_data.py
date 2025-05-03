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
        latest = data.iloc[-1]
        previous = data.iloc[-2]

        if close_col not in latest or close_col not in previous:
            market_summary.append(f"⚠️ No valid price data for {name}. Check the data.")
            continue

        price = float(latest[close_col])
        prev_price = float(previous[close_col])

        if prev_price == 0:
            market_summary.append(f"⚠️ Previous price is zero for {name}, cannot compute change.")
            continue

        change = ((price - prev_price) / prev_price) * 100
        # Further logic to handle VIX, Gold, and other conditions
        # (same as your current code)
    
    except Exception as e:
        market_summary.append(f"❌ Error fetching *{name}* ({ticker}): {e}")
        continue
