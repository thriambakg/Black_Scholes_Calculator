import streamlit as st
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(to_email, stock_symbol, price_point, current_price):
    """
    Sends an email alert to the user.
    """
    # Fetch credentials from Streamlit secrets
    from_email = st.secrets["email_credentials"]["EMAIL_ADDRESS"]
    email_password = st.secrets["email_credentials"]["EMAIL_PASSWORD"]
    
    subject = f"Stock Alert: {stock_symbol} Price Threshold Reached"
    body = (
        f"Hello,\n\n"
        f"The stock {stock_symbol} has reached your threshold.\n"
        f"Current Price: ${current_price:.2f}\n"
        f"Threshold: ${price_point:.2f}\n\n"
        f"Regards,\nYour Stock Alert App"
    )
    
    # Create email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        # Send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, email_password)
        server.send_message(msg)
        print(f"Email alert sent to {to_email} about {stock_symbol}.")
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

def monitor_stock(to_email, stock_symbol, price_point, comparison_mode):
    """
    Monitors the stock price and sends an email alert based on the comparison mode.
    
    Parameters:
        to_email (str): Recipient email address.
        stock_symbol (str): Stock ticker symbol.
        price_point (float): Price threshold.
        comparison_mode (int): 1 for greater-than check, 0 for less-than check.
    """
    try:
        # Fetch real-time stock data
        stock = yf.Ticker(stock_symbol)
        stock_info = stock.history(period="1d", interval="1m")  # Fetch real-time minute-level data
        current_price = stock_info["Close"].iloc[-1]
        
        # Check price threshold based on comparison mode
        if comparison_mode == 1 and current_price >= price_point:
            send_email_alert(to_email, stock_symbol, price_point, current_price)
        elif comparison_mode == 0 and current_price <= price_point:
            send_email_alert(to_email, stock_symbol, price_point, current_price)
        else:
            comparison_str = "above" if comparison_mode == 1 else "below"
            print(f"{stock_symbol} is currently at ${current_price:.2f}, not {comparison_str} the threshold of ${price_point:.2f}.")
    except Exception as e:
        print(f"Error fetching stock data: {e}")

# # Streamlit App UI
# st.title("Stock Price Monitor")

# # Inputs for the Streamlit app
# user_email = st.text_input("Enter your email address for alerts:")
# stock_to_monitor = st.text_input("Enter the stock symbol to monitor (e.g., AAPL):")
# price_threshold = st.number_input("Enter the price threshold to trigger an alert:", min_value=0.0, step=0.01)

# if st.button("Start Monitoring"):
#     if user_email and stock_to_monitor and price_threshold:
#         st.write(f"Monitoring {stock_to_monitor} for price threshold ${price_threshold:.2f}.")
#         monitor_stock(user_email, stock_to_monitor, price_threshold)
#     else:
#         st.error("Please fill in all fields to start monitoring.")
