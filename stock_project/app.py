from flask import Flask
from flask_cors import CORS
from stock_price_prediction.routes import stock_bp
from sentiment_analysis.routes import sentiment_bp
from portfolio_optimization.routes import portfolio_optimization_bp
from loss_averaging.routes import loss_averaging_bp

app = Flask(__name__)

# Enable CORS for all routes and all origins (specifically for React at localhost:3000)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Register Blueprints
app.register_blueprint(stock_bp, url_prefix='/api')
app.register_blueprint(sentiment_bp, url_prefix='/api')
app.register_blueprint(portfolio_optimization_bp, url_prefix='/api')
app.register_blueprint(loss_averaging_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
