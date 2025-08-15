// src/components/HomePage.js

import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div>
      <h1>Welcome to the Stock Optimization App</h1>
      <nav>
        <ul>
          <li><Link to="/portfolio-optimization">Portfolio Optimization</Link></li>
          <li><Link to="/loss-averaging">Loss Averaging</Link></li>
          <li><Link to="/stock-price-prediction">Stock Price Prediction</Link></li>
          <li><Link to="/stock-sentiment-analysis">Stock Sentiment Analysis</Link></li>
        </ul>
      </nav>
    </div>
  );
}

export default HomePage;
