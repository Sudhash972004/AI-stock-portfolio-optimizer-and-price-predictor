import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './HomePage';
import PortfolioOptimization from './PortfolioOptimization';
import LossAveraging from './LossAveraging';
import StockPricePrediction from './StockPricePrediction';
import StockSentimentAnalysis from './StockSentimentAnalysis';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/portfolio-optimization" element={<PortfolioOptimization />} />
        <Route path="/loss-averaging" element={<LossAveraging />} />
        <Route path="/stock-price-prediction" element={<StockPricePrediction />} />
        <Route path="/stock-sentiment-analysis" element={<StockSentimentAnalysis />} />
      </Routes>
    </Router>
  );
}

export default App;
