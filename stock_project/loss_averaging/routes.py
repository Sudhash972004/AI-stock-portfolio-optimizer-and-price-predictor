from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import yfinance as yf

loss_averaging_bp = Blueprint('loss_averaging', __name__)

def fetch_stock_price(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        current_price = stock.history(period="1d")["Close"].iloc[-1]
        return round(current_price, 2)
    except Exception as e:
        print(f"Error fetching stock price: {e}")
        return None

def calculate_loss_averaging(stock_symbol, avg_price, num_shares, invest_amount):
    current_price = fetch_stock_price(stock_symbol)
    if current_price is None:
        return {"message": "Failed to fetch current price. Try again."}

    total_cost_price = avg_price * num_shares
    total_current_value = current_price * num_shares
    amount_loss = total_cost_price - total_current_value
    percentage_loss = (amount_loss / total_cost_price) * 100 if total_cost_price != 0 else 0

    threshold_price = avg_price * 0.85
    if current_price >= threshold_price:
        return {
            "message": "No loss averaging needed. The price hasn't fallen enough.",
            "current_price": current_price,
            "percentage_loss": round(percentage_loss, 2),
            "amount_loss": round(amount_loss, 2)
        }

    additional_shares = invest_amount // current_price
    if additional_shares == 0:
        return {
            "message": "Investment amount is too low to buy any shares.",
            "current_price": current_price
        }

    new_total_shares = num_shares + additional_shares
    total_cost = total_cost_price + (additional_shares * current_price)
    new_avg_price = total_cost / new_total_shares

    message = (
        f"📉 Current loss: {round(percentage_loss, 2)}% (₹{round(amount_loss, 2)} total loss).\n"
        f"📌 Buy {additional_shares} more shares at ₹{current_price}.\n"
        f"📊 New Average Price: ₹{round(new_avg_price, 2)}\n"
        f"📈 Total Shares After Purchase: {new_total_shares}"
    )

    return {
        "message": message,
        "current_price": current_price,
        "percentage_loss": round(percentage_loss, 2),
        "amount_loss": round(amount_loss, 2),
        "additional_shares": int(additional_shares),
        "new_avg_price": round(new_avg_price, 2),
        "total_shares": int(new_total_shares)
    }

@loss_averaging_bp.route('/loss-averaging', methods=['POST', 'OPTIONS'])
@cross_origin(origin='http://localhost:3000', methods=['POST', 'OPTIONS'], allow_headers=['Content-Type'])
def handle_loss_averaging():
    if request.method == 'OPTIONS':
        return '', 200  # Preflight request passes

    data = request.get_json()

    try:
        stock_symbol = data.get('stock_symbol')
        avg_price = float(data.get('avg_price'))
        num_shares = int(data.get('num_shares'))
        invest_amount = float(data.get('invest_amount'))

        if not stock_symbol or avg_price <= 0 or num_shares <= 0 or invest_amount <= 0:
            return jsonify({"message": "Invalid input. Please check your values."}), 400

        result = calculate_loss_averaging(stock_symbol, avg_price, num_shares, invest_amount)
        return jsonify(result)

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
