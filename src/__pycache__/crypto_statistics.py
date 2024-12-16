import cryptocompare
import pandas as pd
import numpy as np
from datetime import datetime
#1
# Function to fetch cryptocurrency statistics
def get_crypto_stats(selected_crypto_symbol, period=365):
    try:
        # Fetch historical data for the selected crypto from CryptoCompare
        data = cryptocompare.get_historical_price_day(
            selected_crypto_symbol,  # Ticker symbol (e.g., 'BTC')
            currency='USD',
            limit=period,  # Fetch `period` days of data
            toTs=int(datetime.now().timestamp())
        )
        
        # Convert the data to a DataFrame for easier handling
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        # Ensure the DataFrame has enough data to calculate statistics
        if len(df) < 2:
            return {"error": "Not enough data to calculate statistics"}

        # Calculate today's return and percentage change
        current_price = df['close'].iloc[-1]  # Use `.iloc` for positional indexing
        previous_price = df['close'].iloc[-2]
        price_change_24h = (current_price - previous_price) / previous_price * 100

        # Calculate the annual return based on the first and last price of the year
        start_price = df['close'].iloc[0]  # Use `.iloc` for the first row
        annual_return = (current_price - start_price) / start_price * 100

        # Calculate annualized volatility (standard deviation of daily returns)
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        volatility = df['log_return'].std() * (252 ** 0.5)  # Annualized volatility (252 trading days)

        # Return the statistics as a dictionary
        stats = {
            "current_price": current_price,
            "price_change_24h": price_change_24h,
            "annual_return": annual_return,
            "volatility": volatility * 100  # Convert to percentage
        }
        return stats
    except Exception as e:
        return {"error": f"Error fetching data for {selected_crypto_symbol}: {str(e)}"}
