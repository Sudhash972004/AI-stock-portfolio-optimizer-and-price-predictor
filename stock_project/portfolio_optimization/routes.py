import yfinance as yf
import yahooquery as yq
import numpy as np
from flask import Blueprint, request, jsonify

portfolio_optimization_bp = Blueprint('portfolio_optimization', __name__)

# Function to fetch data from YahooQuery or YahooFinance
def fetch_data(stock_symbol):
    try:
        # First attempt with yahooquery
        stock = yq.Ticker(stock_symbol)
        data = stock.history(period="5y")
        if data.empty or 'adjclose' not in data.columns:
            raise ValueError("Invalid yahooquery data")
        return data
    except Exception as e:
        try:
            # Fallback to yfinance if yahooquery fails
            data = yf.download(stock_symbol, period="5y")
            if data.empty or 'Adj Close' not in data.columns:
                raise ValueError("Invalid yfinance data")
            return data
        except Exception as e:
            print(f"Error fetching data for {stock_symbol}: {e}")
            return None

# Function to calculate returns and volatility
def calculate_returns_and_volatility(data):
    if 'Adj Close' in data.columns:
        returns = data['Adj Close'].pct_change().dropna()
    elif 'adjclose' in data.columns:
        returns = data['adjclose'].pct_change().dropna()
    else:
        raise ValueError("Missing price column")
    
    if returns.empty:
        return 0.0, 0.0
    
    # Calculate annualized return and volatility (standard deviation)
    return returns.mean() * 252, returns.std() * np.sqrt(252)

# Function to fetch the revenue growth
def fetch_revenue_growth(symbol):
    try:
        stock = yf.Ticker(symbol)
        growth = stock.info.get("revenueGrowth", 0)
        return float(growth) * 100 if growth is not None else 0.0
    except Exception as e:
        print(f"Error fetching revenue growth for {symbol}: {e}")
        return 0.0

# Portfolio optimization logic
def optimize_portfolio(tickers, total_investment):
    stock_data = []
    prices = {}
    fundamentals = {}

    for ticker in tickers:
        data = fetch_data(ticker)
        if data is None:
            return {"error": f"Data fetch failed for {ticker}"}

        try:
            expected_return, volatility = calculate_returns_and_volatility(data)
        except Exception as e:
            return {"error": f"Error calculating returns for {ticker}: {str(e)}"}

        growth = fetch_revenue_growth(ticker)
        fundamentals[ticker] = {"Revenue_Growth_5Y": round(growth, 2)}

        # Ensure positive values for expected return, volatility, and growth
        expected_return = max(expected_return, 0)
        volatility = max(volatility, 0.0001)  # Avoid division by zero
        growth = max(growth, 0)

        # Composite score
        score = (expected_return * 0.5 + growth * 0.5) / volatility
        price = yf.Ticker(ticker).history(period="1d")["Close"][-1]
        prices[ticker] = price
        stock_data.append({
            "ticker": ticker,
            "score": score,
            "price": price
        })

    # Normalize scores to get weights
    total_score = sum(stock["score"] for stock in stock_data)
    if total_score == 0:
        weight = 1 / len(stock_data)
        for s in stock_data:
            s["weight"] = weight
    else:
        for s in stock_data:
            s["weight"] = s["score"] / total_score

    allocation = {}
    total_spent = 0

    for s in stock_data:
        amount = total_investment * s["weight"]
        shares = np.floor(amount / s["price"])
        spent = shares * s["price"]
        total_spent += spent
        allocation[s["ticker"]] = {
            "shares": int(shares),
            "allocated_money": round(spent, 2),
            "current_price": round(s["price"], 2)
        }

    leftover = round(total_investment - total_spent, 2)

    return {
        "allocation": allocation,
        "expected_annual_return": round(np.mean([calculate_returns_and_volatility(fetch_data(s["ticker"]))[0] for s in stock_data]) * 100, 2),
        "annual_risk": round(np.mean([calculate_returns_and_volatility(fetch_data(s["ticker"]))[1] for s in stock_data]) * 100, 2),
        "leftover_amount": leftover,
        "fundamentals": fundamentals  # Adding fundamentals
    }

@portfolio_optimization_bp.route('/portfolio-optimize', methods=['POST'])
def portfolio_optimize():
    try:
        data = request.get_json()
        tickers = data.get("stocks", [])
        investment = data.get("investment", 0)

        if not tickers or investment <= 0:
            return jsonify({"error": "Invalid input"}), 400

        result = optimize_portfolio(tickers, investment)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 
