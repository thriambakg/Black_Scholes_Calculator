import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Import custom modules
from crypto_statistics import get_crypto_stats
from risk_return import (
    calculate_portfolio_metrics,
    calculate_correlation,
)

# Caching Strategy for Expensive Computations
@st.cache_data(ttl=3600)  # Cache results for 1 hour
def cached_fetch_volatility(_fetch_function, ticker, period):
    """
    Cached wrapper for volatility fetching
    
    Args:
        _fetch_function (callable): The volatility fetching function
        ticker (str): Stock ticker symbol
        period (str): Time period for volatility calculation
    
    Returns:
        float: Volatility value
    """
    return _fetch_function(ticker, period)

@st.cache_data(ttl=86400)  # Cache crypto stats for 24 hours
def cached_get_crypto_stats(symbol, period):

    """
    Cached wrapper for cryptocurrency statistics
    
    Args:
        symbol (str): Cryptocurrency symbol
        period (int): Time period in days
        @st.cache_data(ttl=86400)  # Cache for 24 hours
    
    Returns:
        dict: Cryptocurrency statistics
    """
    print(f"Cache Miss - Fetching data for {symbol} with period {period}")
    return get_crypto_stats(symbol, period)

@st.cache_data(ttl=3600)
def safe_fetch_stock_price(ticker):
    """
    Safely fetch current stock price with caching
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        float or None: Current stock price or None if error
    """
    try:
        stock = yf.Ticker(ticker.upper())
        return stock.history(period="1d")["Close"].iloc[-1]
    except Exception as e:
        st.error(f"Error fetching price for {ticker}: {e}")
        return None

@st.cache_data(ttl=3600)
def cached_portfolio_metrics(portfolio_tuples, period="1y", risk_free_rate=0.05):
    """
    Cached wrapper for portfolio metrics calculation
    
    Args:
        portfolio_tuples (list): List of tuples with (stock_ticker, number_of_shares, current_price)
        period (str): Time period for analysis
        risk_free_rate (float): Risk-free rate for Sharpe ratio calculation
    
    Returns:
        dict: Portfolio metrics including risk, return, and stock details
    """
    try:
        return calculate_portfolio_metrics(portfolio_tuples, period, risk_free_rate)
    except Exception as e:
        st.error(f"Error calculating portfolio metrics: {e}")
        return None

@st.cache_data(ttl=3600)
def cached_correlation_matrix(tickers, period="1y"):
    """
    Cached wrapper for correlation matrix calculation
    
    Args:
        tickers (list): List of stock tickers
        period (str): Time period for correlation calculation
    
    Returns:
        pd.DataFrame: Correlation matrix
    """
    try:
        return calculate_correlation(tickers, period)
    except Exception as e:
        st.error(f"Error calculating correlation matrix: {e}")
        return None

def initialize_session_state():
    """
    Centralize and standardize session state initialization
    """
    default_states = {
        "time_frame": "1y",
        "portfolio_risk_entries": [{"stock": "", "shares": 0.0}],
        "portfolio_risk_results": None,
        "current_volatility_ticker": "AAPL",
        "current_volatility": None,
        "crypto_stats": None,
        "heatmap_params": {
            "min_S": None,
            "max_S": None,
            "min_sigma": None,
            "max_sigma": None,
        },
        "heatmaps": None,
        "selected_crypto": "BTC",
        "correlation_matrix": None,
        "portfolio_metrics_cache": None
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

@st.cache_data(ttl=3600)
def get_portfolio_performance_metrics(portfolio_tuples, period="1y"):
    """
    Cached wrapper for getting comprehensive portfolio performance metrics
    
    Args:
        portfolio_tuples (list): List of tuples with (stock_ticker, number_of_shares, current_price)
        period (str): Time period for analysis
    
    Returns:
        dict: Complete portfolio analysis including correlations and risk metrics
    """
    try:
        # Get basic portfolio metrics
        metrics = cached_portfolio_metrics(portfolio_tuples, period)
        if not metrics:
            return None

        # Get correlation matrix for portfolio stocks
        tickers = [t[0] for t in portfolio_tuples]
        correlation = cached_correlation_matrix(tickers, period)
        
        # Combine all metrics
        complete_metrics = {
            **metrics,
            'correlation_matrix': correlation.to_dict() if correlation is not None else None,
            'analysis_period': period,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return complete_metrics
    except Exception as e:
        st.error(f"Error calculating portfolio performance metrics: {e}")
        return None

@st.cache_data(ttl=3600)
def get_crypto_market_data(symbols, period=365):
    """
    Cached wrapper for getting multiple cryptocurrency statistics
    
    Args:
        symbols (list): List of cryptocurrency symbols
        period (int): Time period in days
    
    Returns:
        dict: Dictionary of cryptocurrency statistics
    """
    try:
        crypto_data = {}
        for symbol in symbols:
            stats = cached_get_crypto_stats(symbol, period)
            if 'error' not in stats:
                crypto_data[symbol] = stats
        return crypto_data
    except Exception as e:
        st.error(f"Error fetching cryptocurrency market data: {e}")
        return None