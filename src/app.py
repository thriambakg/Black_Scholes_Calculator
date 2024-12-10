import streamlit as st
from black_scholes import black_scholes
from volatility_fetcher import fetch_volatility
from heatmap_generator import generate_heatmaps

# Set page config
st.set_page_config(layout="wide", page_title="Black-Scholes Calculator", page_icon="📈")

# Predefined list of stock tickers for suggestions (can be expanded)
STOCK_TICKERS = [
    "AAPL", "TSLA", "GOOGL", "AMZN", "MSFT", "META", "NFLX", "NVDA", "SPY", "VTI",
    "MSCI", "BA", "GE", "INTC", "IBM", "DIS", "GS", "WMT", "JPM", "BABA"
]

st.title("Black-Scholes Option Pricing Calculator")

# Add a section for stock volatility search above the main content
st.header("Stock Volatility Fetcher")

# Search Bar for Stock Ticker with Suggestions
ticker_input = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, TSLA)", value="AAPL")
search_suggestions = [ticker for ticker in STOCK_TICKERS if ticker.startswith(ticker_input.upper())]

# Display search suggestions if there are any
if search_suggestions:
    st.write("Suggestions: ", ", ".join(search_suggestions))

fetch_volatility_button = st.button("Fetch Volatility")

# Display Volatility
volatility_display = st.empty()

# Fetch volatility when button is clicked
if fetch_volatility_button and ticker_input:
    try:
        volatility = fetch_volatility(ticker_input)
        volatility_display.markdown(f"**Volatility for {ticker_input.upper()}:** {volatility:.4f}")
    except Exception as e:
        volatility_display.markdown(f"Error fetching volatility: {str(e)}")

# Divider line
st.markdown("---")

# Sidebar Inputs for the Black-Scholes formula
st.sidebar.header("Input Parameters for Option Pricing")
S = st.sidebar.number_input("Current Stock Price (S)", min_value=0.0, step=1.0, value=100.0)
K = st.sidebar.number_input("Strike Price (K)", min_value=0.0, step=1.0, value=110.0)
T = st.sidebar.number_input("Time to Maturity (T) (in years)", min_value=0.01, step=0.01, value=1.0)
r = st.sidebar.number_input("Risk-Free Interest Rate (r) (as a decimal)", min_value=0.0, step=0.01, value=0.05)
sigma = st.sidebar.number_input("Volatility (σ) (as a decimal)", min_value=0.0, step=0.01, value=0.2)

# Create empty spaces for live readings of call and put prices
call_price_placeholder = st.empty()
put_price_placeholder = st.empty()

# Update live reading of option prices
def update_option_prices():
    call_price = black_scholes(S, K, T, r, sigma, option_type="call")
    put_price = black_scholes(S, K, T, r, sigma, option_type="put")
    
    # Display the updated option prices in the placeholders with custom styling
    call_price_placeholder.markdown(f"""
    <div style="background-color: green; color: white; padding: 20px; text-align: center; font-size: 24px; border-radius: 10px;">
        Call Option Price: ${call_price:.2f}
    </div>
    """, unsafe_allow_html=True)
    
    put_price_placeholder.markdown(f"""
    <div style="background-color: red; color: white; padding: 20px; text-align: center; font-size: 24px; border-radius: 10px;">
        Put Option Price: ${put_price:.2f}
    </div>
    """, unsafe_allow_html=True)

# Initial update to show prices when inputs change
update_option_prices()

# Divider line
st.markdown("---")

# Heatmap Functionality
st.header("Heatmaps: Option Price as a Function of Stock Price and Volatility")
st.write(
    "Visualize how Call and Put option prices change with different stock prices and volatilities."
)

# Sidebar Inputs for the Heatmap
st.sidebar.header("Heatmap Parameters")
min_S = st.sidebar.number_input("Minimum Stock Price (S)", min_value=0.0, step=1.0, value=50.0)
max_S = st.sidebar.number_input("Maximum Stock Price (S)", min_value=0.0, step=1.0, value=150.0)
min_sigma = st.sidebar.slider("Minimum Volatility (σ)", 0.01, 1.0, 0.1)
max_sigma = st.sidebar.slider("Maximum Volatility (σ)", 0.01, 1.0, 0.5)

# Generate and display the heatmaps
heatmaps = generate_heatmaps(S, K, T, r, min_S, max_S, min_sigma, max_sigma)
st.plotly_chart(heatmaps["call"], use_container_width=True)
st.plotly_chart(heatmaps["put"], use_container_width=True)

# Add LinkedIn profile link
st.markdown("---")
st.write("Made by [Thriambak Giriprakash MBA, SWE](https://www.linkedin.com/in/thriambakg/)")
