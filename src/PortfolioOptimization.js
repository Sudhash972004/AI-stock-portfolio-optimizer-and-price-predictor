import React, { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

const PortfolioOptimization = () => {
  const [stocks, setStocks] = useState("");
  const [investment, setInvestment] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // State for loading

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true); // Start loading when the submit button is clicked
    try {
      const response = await fetch("http://localhost:5000/api/portfolio-optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          stocks: stocks.split(",").map((s) => s.trim()),
          investment: parseFloat(investment),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch data");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false); // Stop loading after the API call is completed
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto text-gray-800">
      <h1 className="text-2xl font-bold mb-4">📈 Portfolio Optimization</h1>

      <form onSubmit={handleSubmit} className="mb-6">
        <input
          type="text"
          placeholder="Stock symbols (comma-separated)"
          value={stocks}
          onChange={(e) => setStocks(e.target.value)}
          className="border px-3 py-2 mr-2 w-2/3 rounded"
        />
        <input
          type="number"
          placeholder="Investment amount"
          value={investment}
          onChange={(e) => setInvestment(e.target.value)}
          className="border px-3 py-2 mr-2 w-1/4 rounded"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Optimize Portfolio
        </button>
      </form>

      {loading && <p className="text-blue-600">Loading...</p>} {/* Display loading message */}

      {error && <p className="text-red-600 mb-4">{error}</p>}

      {result && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Optimized Portfolio Allocation</h2>

          {Object.entries(result.allocation).map(([ticker, info]) => (
            <div key={ticker} className="mb-4 p-3 border rounded bg-gray-50">
              <h3 className="font-semibold">{ticker}</h3>
              <p>Allocated: ₹{info.allocated_money.toLocaleString()}</p>
              <p>Shares: {info.shares}</p>
              <p>Current Price: ₹{info.current_price}</p>
              <p><strong>Revenue Growth:</strong> {result.fundamentals[ticker]?.Revenue_Growth_5Y || "Data Not Available"}</p>
            </div>
          ))}

          <div className="mt-6">
            <h3 className="text-lg font-semibold">📊 Allocation Pie Chart</h3>
            <PieChart width={300} height={240}>
              <Pie
                data={Object.entries(result.allocation).map(([ticker, info]) => ({
                  name: ticker,
                  value: info.allocated_money,
                }))}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                label
              >
                {Object.entries(result.allocation).map(([ticker, info], index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
          <div className="mt-4">
            <p><strong>Expected Annual Return:</strong> {result.expected_annual_return}%</p>
            <p><strong>Annual Risk (Volatility):</strong> {result.annual_risk}%</p>
            <p><strong>Leftover Amount:</strong> ₹{result.leftover_amount}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioOptimization;
