import yfinance as yf
import numpy as np
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_portfolio_metrics(portfolio_tuples, risk_free_rate=0.05):
    """
    Calculate portfolio risk and expected return.
    
    Args:
    portfolio_tuples (list): List of tuples with (stock_ticker, number_of_shares, current_price)
    risk_free_rate (float): Annual risk-free rate (default 5%)
    
    Returns:
    dict: Portfolio metrics including total risk, expected return, and individual stock details
    """
    # Validate input
    if not portfolio_tuples:
        raise ValueError("Portfolio cannot be empty")
    
    # Prepare data structures
    stock_tickers = [ticker for ticker, _, _ in portfolio_tuples]
    
    # Calculate total portfolio value
    total_portfolio_value = sum([shares * price for _, shares, price in portfolio_tuples])
    
    # Download historical stock data
    try:
        stock_data = yf.download(stock_tickers, period="5y")['Adj Close']
        logger.info(f"Successfully downloaded data for {stock_tickers}")
    except Exception as e:
        logger.error(f"Error downloading stock data: {e}")
        raise ValueError(f"Error downloading stock data: {e}")
    
    # Ensure data is present for all stocks
    if stock_data.empty:
        raise ValueError("No stock data could be retrieved. Check stock tickers.")
    
    # Calculate returns
    returns = stock_data.pct_change().dropna()
    
    # Individual stock analysis
    stock_details = {}
    portfolio_weights = []
    expected_returns = []
    stock_variances = []
    
    for ticker, shares, current_price in portfolio_tuples:
        # Skip if data is insufficient
        if ticker not in returns.columns:
            logger.warning(f"No data available for {ticker}")
            continue
        
        # Calculate individual stock metrics
        stock_returns = returns[ticker]
        avg_annual_return = stock_returns.mean() * 252  # Annualized return
        annual_volatility = stock_returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Calculate portfolio weight
        stock_value = shares * current_price
        weight = stock_value / total_portfolio_value
        portfolio_weights.append(weight)
        expected_returns.append(avg_annual_return)
        stock_variances.append(annual_volatility ** 2)
        
        # Store stock details
        stock_details[ticker] = {
            'shares': shares,
            'current_price': current_price,
            'total_value': stock_value,
            'annual_return': avg_annual_return,
            'annual_volatility': annual_volatility,
            'weight': weight
        }
    
    # Validate calculations
    if not stock_details:
        raise ValueError("Unable to calculate metrics for any stocks in the portfolio")
    
    # Portfolio expected return (weighted average of individual returns)
    portfolio_expected_return = np.dot(portfolio_weights, expected_returns)
    
    # Portfolio variance calculation (including covariance)
    correlation_matrix = returns.corr()

    std_devs = returns.std()  # Calculate standard deviation (volatility) of each stock's returns
    covariance_matrix = correlation_matrix * np.outer(std_devs, std_devs)
    portfolio_variance = np.dot(
    np.dot(portfolio_weights, covariance_matrix.loc[stock_tickers, stock_tickers].values), 
    portfolio_weights
    )
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    # Sharpe Ratio calculation
    sharpe_ratio = (portfolio_expected_return - risk_free_rate) / portfolio_volatility
    
    return {
        'total_portfolio_value': total_portfolio_value,
        'portfolio_expected_return': portfolio_expected_return * 100,  # Convert to percentage
        'portfolio_volatility': portfolio_volatility * 100,  # Convert to percentage
        'sharpe_ratio': sharpe_ratio,
        'stock_details': stock_details,
        'individual_stocks': stock_tickers
    }

def main(portfolio_tuples):
    """
    Main function to process portfolio tuples and print results.
    
    Args:
    portfolio_tuples (list): List of tuples with (stock_ticker, number_of_shares, current_price)
    """
    try:
        # Calculate portfolio metrics
        portfolio_metrics = calculate_portfolio_metrics(portfolio_tuples)
        
        # Print formatted results
        print("\n--- Portfolio Analysis ---")
        print(f"Total Portfolio Value: ${portfolio_metrics['total_portfolio_value']:,.2f}")
        print(f"Portfolio Expected Annual Return: {portfolio_metrics['portfolio_expected_return']:.2f}%")
        print(f"Portfolio Volatility (Risk): {portfolio_metrics['portfolio_volatility']:.2f}%")
        print(f"Sharpe Ratio: {portfolio_metrics['sharpe_ratio']:.2f}")
        
        print("\nIndividual Stock Details:")
        for ticker, details in portfolio_metrics['stock_details'].items():
            print(f"\n{ticker}:")
            print(f"  Shares: {details['shares']}")
            print(f"  Current Price: ${details['current_price']:.2f}")
            print(f"  Total Value: ${details['shares'] * details['current_price']:,.2f}")
            print(f"  Weight: {details['weight']*100:.2f}%")
            print(f"  Annual Return: {details['annual_return']*100:.2f}%")
            print(f"  Annual Volatility: {details['annual_volatility']*100:.2f}%")
        
        return portfolio_metrics
    
    except Exception as e:
        print(f"Error calculating portfolio metrics: {e}")
        logger.error(f"Portfolio calculation failed: {e}")
        return None

# Allow direct script execution for testing
if __name__ == "__main__":
    # Example usage for testing
    test_portfolio = [
        ('AAPL', 10, 190.50),  # ticker, shares, current price
        ('GOOGL', 5, 125.75),
        ('MSFT', 7, 340.20)
    ]
    main(test_portfolio)