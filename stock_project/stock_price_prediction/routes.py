# stock_price_prediction/routes.py
from flask import Blueprint, request, jsonify
import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from sklearn.metrics import mean_absolute_error, mean_squared_error
from yahooquery import Ticker
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

stock_bp = Blueprint('stock_price_prediction', __name__)

def fetch_stock_data(symbol, start="2019-01-01"):
    stock = Ticker(symbol)
    data = stock.history(start=start).reset_index()
    if data.empty:
        raise ValueError("No data found. Check the stock symbol or date range.")
    
    data['date'] = pd.to_datetime(data['date'], utc=True, errors='coerce').dt.tz_convert(None)
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    data['EMA_20'] = data['close'].ewm(span=20, adjust=False).mean()
    data = data.bfill()
    return data[['date', 'open', 'close', 'volume', 'SMA_50', 'EMA_20']]

def create_sequences(data, time_step=100):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:i+time_step])
        y.append(data[i+time_step, 1])
    return np.array(X), np.array(y)

def predict_future_days(model, last_seq, future_days=100):
    future_preds = []
    seq = last_seq.copy()
    for _ in range(future_days):
        pred = model.predict(seq.reshape(1, seq.shape[0], seq.shape[1]), verbose=0)[0, 0]
        future_preds.append(pred)
        new_day = seq[-1].copy()
        new_day[1] = pred
        seq = np.vstack((seq[1:], new_day))
    return np.array(future_preds)

def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    base64_img = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return base64_img

@stock_bp.route('/predict_stock', methods=['POST'])
def predict_stock():
    data = request.get_json()
    symbol = data.get('symbol')

    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400

    try:
        df = fetch_stock_data(symbol)
        df.set_index('date', inplace=True)

        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(df[['open', 'close', 'volume', 'SMA_50', 'EMA_20']])

        time_step = 100
        X, y = create_sequences(scaled_data, time_step)
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        model = Sequential([
            Bidirectional(LSTM(256, return_sequences=True, input_shape=(time_step, 5))),
            Dropout(0.3),
            Bidirectional(LSTM(128)),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X_train, y_train, epochs=2, batch_size=32, verbose=0)

        predicted_test = model.predict(X_test, verbose=0)
        pred_matrix = np.zeros((predicted_test.shape[0], 5))
        pred_matrix[:, 1] = predicted_test[:, 0]
        predicted_prices_original = scaler.inverse_transform(pred_matrix)[:, 1]

        y_matrix = np.zeros((y_test.shape[0], 5))
        y_matrix[:, 1] = y_test
        y_test_original = scaler.inverse_transform(y_matrix)[:, 1]

        mae = mean_absolute_error(y_test_original, predicted_prices_original)
        mse = mean_squared_error(y_test_original, predicted_prices_original)
        rmse = np.sqrt(mse)

        # Plot actual vs predicted
        test_dates = df.index[-len(y_test_original):]
        fig1 = plt.figure(figsize=(12, 6))
        plt.plot(test_dates, y_test_original, label="Actual")
        plt.plot(test_dates, predicted_prices_original, label="Predicted", linestyle='dashed')
        plt.title(f"{symbol} - Actual vs Predicted")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        actual_graph = plot_to_base64(fig1)

        # Future prediction
        last_sequence = scaled_data[-time_step:]
        future_preds = predict_future_days(model, last_sequence)
        future_matrix = np.zeros((future_preds.shape[0], 5))
        future_matrix[:, 1] = future_preds
        future_predictions_original = scaler.inverse_transform(future_matrix)[:, 1]

        last_date = df.index[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=100)

        fig2 = plt.figure(figsize=(12, 6))
        last_known_price = df['close'].iloc[-1]
        plt.plot([last_date, future_dates[0]], [last_known_price, future_predictions_original[0]], 
                 linestyle='dotted', color='green')
        plt.plot(future_dates, future_predictions_original, label="Future Predictions", 
                 linestyle='dotted', color='green')
        plt.axvline(x=last_date, color='gray', linestyle='--', linewidth=1)
        plt.title(f"{symbol} - Future 100 Day Forecast")
        plt.xlabel("Date")
        plt.ylabel("Predicted Price")
        plt.legend()
        future_graph = plot_to_base64(fig2)

        return jsonify({
            'mae': round(mae, 2),
            'mse': round(mse, 2),
            'rmse': round(rmse, 2),
            'actual_vs_predicted_graph': actual_graph,
            'future_prediction_graph': future_graph
        })

    except Exception as e:
        return jsonify({'error': f"Prediction failed: {str(e)}"}), 500
