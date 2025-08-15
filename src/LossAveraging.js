import React, { useState } from 'react';

function LossAveraging() {
  const [stockSymbol, setStockSymbol] = useState('');
  const [avgPrice, setAvgPrice] = useState('');
  const [numShares, setNumShares] = useState('');
  const [investAmount, setInvestAmount] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setError('');
    setLoading(true);

    // Basic Validation
    if (!stockSymbol || avgPrice <= 0 || numShares <= 0 || investAmount <= 0) {
      setError('All inputs must be positive values and stock symbol cannot be empty.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/loss-averaging', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stock_symbol: stockSymbol, // Using dynamic stock symbol
          avg_price: parseFloat(avgPrice), // Using dynamic average price
          num_shares: parseInt(numShares), // Using dynamic number of shares
          invest_amount: parseFloat(investAmount), // Using dynamic investment amount
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Request failed');
      }

      setResult(data);
    } catch (err) {
      console.error('Error:', err);
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setStockSymbol('');
    setAvgPrice('');
    setNumShares('');
    setInvestAmount('');
    setResult(null);
    setError('');
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: 'auto' }}>
      <h1>📉 Loss Averaging</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Stock Symbol:</label>
          <input 
            type="text" 
            value={stockSymbol} 
            onChange={(e) => setStockSymbol(e.target.value)} 
            required 
            disabled={loading} 
          />
        </div>
        <div>
          <label>Average Price (₹):</label>
          <input 
            type="number" 
            value={avgPrice} 
            onChange={(e) => setAvgPrice(e.target.value)} 
            required 
            disabled={loading} 
          />
        </div>
        <div>
          <label>Number of Shares:</label>
          <input 
            type="number" 
            value={numShares} 
            onChange={(e) => setNumShares(e.target.value)} 
            required 
            disabled={loading} 
          />
        </div>
        <div>
          <label>Investment Amount (₹):</label>
          <input 
            type="number" 
            value={investAmount} 
            onChange={(e) => setInvestAmount(e.target.value)} 
            required 
            disabled={loading} 
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Submit'}
        </button>
        {result && <button type="button" onClick={resetForm}>Reset</button>}
      </form>

      <strong>
        {loading && <p>⏳ Please wait...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {result && (
          <div style={{ marginTop: '20px', color: 'green' }}>
            <p><strong>📈 Current Market Price of the Stock:</strong> ₹{result.current_price}</p>
            <p><strong>📉 Percentage of Loss:</strong> {result.percentage_loss}%</p>
            <p><strong>💸 Amount of Loss:</strong> ₹{result.amount_loss}</p>
            {result.additional_shares ? (
              <>
                <p><strong>🛒 Additional Shares You can Buy:</strong> {result.additional_shares}</p>
                <p><strong>📊 New Average Price:</strong> ₹{result.new_avg_price}</p>
                <p><strong>📦 Total Shares You Hold After Purchase:</strong> {result.total_shares}</p>
              </>
            ) : null}
          </div>
        )}
      </strong>
    </div>
  );
}

export default LossAveraging;
