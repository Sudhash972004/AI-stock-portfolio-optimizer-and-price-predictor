import React, { useState } from "react";

function StockSentiment() {
  const [stockSymbol, setStockSymbol] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchSentiment = async () => {
    if (!stockSymbol) return;
    setLoading(true);
    setData(null);

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/news?symbol=${stockSymbol}`);
      const result = await response.json();
      console.log("API Response:", result);
      setData(result);
    } catch (error) {
      console.error("Error fetching sentiment:", error);
      setData({ error: "Error fetching data" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Stock Sentiment Analysis</h1>
      <input
        type="text"
        placeholder="Enter Stock Symbol (e.g., RELIANCE.NS)"
        value={stockSymbol}
        onChange={(e) => setStockSymbol(e.target.value)}
      />
      <button onClick={fetchSentiment}>Get Sentiment</button>

      {loading && <p>Loading...</p>}

      {data && !data.error && (
        <div>
          <h2>Stock: {data.stock}</h2>

          <h3>Fundamental Analysis:</h3>
          {data.fundamental_analysis ? (
            Object.entries(data.fundamental_analysis).map(([key, value]) =>
              key !== "Overall Classification" ? (
                <p key={key}>
                  {key}: <strong>{value}</strong>
                </p>
              ) : null
            )
          ) : (
            <p>No fundamental data available.</p>
          )}

          <h3>
            Overall Fundamentals:{" "}
            <span
              style={{
                color:
                  data.fundamental_analysis["Overall Classification"] === "Good"
                    ? "green"
                    : data.fundamental_analysis["Overall Classification"] === "Bad"
                    ? "red"
                    : "orange",
              }}
            >
              {data.fundamental_analysis["Overall Classification"]}
            </span>
          </h3>
          <h3>Overall Sentiment of the News: {data.overall_sentiment}</h3>

          <h3>News Articles:</h3>
          {data.articles && data.articles.length > 0 ? (
            data.articles.map((article, index) => (
              <div key={index}>
                <h4>
                  <a href={article.link} target="_blank" rel="noopener noreferrer">
                    {article.title}
                  </a>
                </h4>
                <p>Sentiment: {article.sentiment}</p>
              </div>
            ))
          ) : (
            <p>No news articles available.</p>
          )}
        </div>
      )}

      {data && data.error && <p>Error: {data.error}</p>}
    </div>
  );
}

export default StockSentiment;
