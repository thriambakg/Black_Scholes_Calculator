import streamlit as st
from black_scholes import black_scholes
from volatility_fetcher import fetch_volatility
from heatmap_generator import generate_heatmaps
from risk_return import main as calculate_portfolio_risk
import yfinance as yf
import pandas as pd

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

st.header("Black-Scholes Calculation")

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

# Calculate the risk of your overall portfolio and your expected rate of return
st.markdown("---")
# Portfolio Risk Calculator Section
st.header("Portfolio Risk Calculator")

# Initialize session state for portfolio entries if not already exists
if 'portfolio_entries' not in st.session_state:
    st.session_state.portfolio_entries = [{"stock": "", "shares": 0}]

# Function to add a new portfolio entry
def add_portfolio_entry():
    st.session_state.portfolio_entries.append({"stock": "", "shares": 0})

# Function to remove the last portfolio entry
def remove_portfolio_entry():
    if len(st.session_state.portfolio_entries) > 1:
        st.session_state.portfolio_entries.pop()

# Portfolio Entry Input Layout
st.write("Enter your stock portfolio:")

# Create input fields for each portfolio entry
for i, entry in enumerate(st.session_state.portfolio_entries):
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        # Stock ticker input with suggestions
        entry['stock'] = st.text_input(
            f"Stock Ticker {i+1}", 
            value=entry['stock'], 
            key=f"stock_input_{i}",
            placeholder="Enter stock ticker (e.g., AAPL)"
        )
    
    with col2:
        # Number of shares input - modified to allow decimal values
        entry['shares'] = st.number_input(
            f"Number of Shares {i+1}", 
            min_value=0.0,  # Changed to float 
            value=float(entry.get('shares', 0.0)),  # Ensure float conversion
            step=0.1,  # Allow increments of 0.1
            key=f"shares_input_{i}",
            format="%.3f"  # Display 3 decimal places
        )
    
    # Remove button for all entries except the first
    if i > 0:
        with col3:
            st.write("") # Align with input
            st.button("➖", key=f"remove_{i}", on_click=remove_portfolio_entry)

# Row of buttons for adding entries and calculating
col1, col2, col3 = st.columns(3)

with col1:
    st.button("Add Stock +", on_click=add_portfolio_entry)

with col2:
    calculate_portfolio = st.button("Calculate Portfolio Risk")

# Placeholder for portfolio risk results
portfolio_results = st.empty()

# Calculate Portfolio Risk
if calculate_portfolio:
    # Fetch current stock prices and calculate total portfolio value
    portfolio_tuples = []
    for entry in st.session_state.portfolio_entries:
        if entry['stock'].strip() and entry['shares'] > 0:
            try:
                # Fetch current stock price
                stock = yf.Ticker(entry['stock'].upper())
                current_price = stock.history(period="1d")['Close'].iloc[-1]
                
                # Create tuple with stock ticker, shares, and current price
                portfolio_tuples.append((
                    entry['stock'].upper(), 
                    entry['shares'], 
                    current_price
                ))
            except Exception as e:
                st.error(f"Error fetching price for {entry['stock']}: {e}")
    
    if portfolio_tuples:
        try:
            # Call the risk_return module's main function
            portfolio_metrics = calculate_portfolio_risk(portfolio_tuples)
            
            # Display results in a more structured way
            if portfolio_metrics:
                portfolio_results.markdown("### Portfolio Analysis Results")
                
                # Create columns for key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Portfolio Value", 
                        f"${portfolio_metrics['total_portfolio_value']:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Expected Annual Return", 
                        f"{portfolio_metrics['portfolio_expected_return']:.2f}%"
                    )
                
                with col3:
                    st.metric(
                        "Portfolio Volatility", 
                        f"{portfolio_metrics['portfolio_volatility']:.2f}%"
                    )

                with col4:
                    st.metric(
                        "Sharpe Ratio", 
                        f"{portfolio_metrics['sharpe_ratio']:.2f}%"
                    )
                
                # Display detailed stock breakdown
                st.subheader("Individual Stock Details")

                # Convert the stock details dictionary into a DataFrame
                stock_details_df = pd.DataFrame.from_dict(
                    {ticker: {
                        'Weight (%)': details['weight'] * 100,
                        'Annual Return (%)': details['annual_return'] * 100,
                        'Annual Volatility (%)': details['annual_volatility'] * 100,
                        'Shares': details['shares'],
                        'Current Price': details['current_price'],
                        'Total Value': details['total_value']
                    } for ticker, details in portfolio_metrics['stock_details'].items()},
                    orient='index'
                )

                # Display the DataFrame in Streamlit
                st.dataframe(stock_details_df.style.format({
                    'Weight (%)': '{:.2f}',
                    'Annual Return (%)': '{:.2f}',
                    'Annual Volatility (%)': '{:.2f}',
                    'Current Price': '${:.2f}',
                    'Total Value': '${:,.2f}'
                }))
        
        except Exception as e:
            portfolio_results.error(f"Error calculating portfolio risk: {str(e)}")
    else:
        portfolio_results.warning("Please enter at least one stock with a valid number of shares.")


# Add LinkedIn profile link
st.markdown("---")
st.write("Made by [Thriambak Giriprakash MBA, SWE](https://www.linkedin.com/in/thriambakg/)")
