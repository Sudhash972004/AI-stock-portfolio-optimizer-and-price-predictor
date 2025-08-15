import React, { useState } from "react";

function StockPrediction() {
  const [symbol, setSymbol] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:5000/predict_stock", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol: symbol.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch prediction");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Error fetching prediction. Please check the stock symbol.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>📈 Stock Price Prediction</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Enter stock symbol (e.g. RELIANCE.NS)"
          required
        />
        <button type="submit">Predict</button>
      </form>

      {loading && <p>⏳ Loading prediction...</p>}

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div>
          <h3>📊 Prediction Results</h3>
          <p><strong>MAE:</strong> {result.mae}</p>
          <p><strong>MSE:</strong> {result.mse}</p>
          <p><strong>RMSE:</strong> {result.rmse}</p>

          <h4>📉 Actual vs Predicted</h4>
          <img
            src={`data:image/png;base64,${result.actual_vs_predicted_graph}`}
            alt="Actual vs Predicted"
            style={{ width: "100%", maxWidth: "700px" }}
          />

          <h4>🔮 Future 100-Day Forecast</h4>
          <img
            src={`data:image/png;base64,${result.future_prediction_graph}`}
            alt="Future Forecast"
            style={{ width: "100%", maxWidth: "700px" }}
          />
        </div>
      )}
    </div>
  );
}

export default StockPrediction;
