from flask import Blueprint, request, jsonify
import requests
import xml.etree.ElementTree as ET
from transformers import pipeline
import torch
from newspaper import Article
from yahooquery import Ticker

sentiment_bp = Blueprint('sentiment_bp', __name__)

device = "cuda" if torch.cuda.is_available() else "cpu"
sentiment_pipeline = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment", device=0 if device == "cuda" else -1)

def extract_full_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error fetching article content: {e}")
        return None

def get_google_news(stock_symbol):
    try:
        url = f"https://news.google.com/rss/search?q={stock_symbol}+stock&hl=en-IN&gl=IN&ceid=IN:en"
        response = requests.get(url)
        if response.status_code != 200:
            return None

        root = ET.fromstring(response.content)
        news_articles = []

        for item in root.findall(".//item")[:5]:
            title = item.find("title").text
            link = item.find("link").text
            full_content = extract_full_article(link)
            content = full_content if full_content else title
            news_articles.append({"title": title, "link": link, "content": content})

        return news_articles if news_articles else None
    except Exception as e:
        print(f"Error fetching Google News: {e}")
        return None

def analyze_sentiment(news_articles):
    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for article in news_articles:
        sentiment = sentiment_pipeline(article["content"])[0]
        score = int(sentiment["label"].split()[0])
        if score >= 4:
            article["sentiment"] = "Positive"
            sentiment_counts["Positive"] += 1
        elif score == 3:
            article["sentiment"] = "Neutral"
            sentiment_counts["Neutral"] += 1
        else:
            article["sentiment"] = "Negative"
            sentiment_counts["Negative"] += 1
    overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
    return news_articles, overall_sentiment

def fetch_fundamental_analysis(stock_symbol):
    try:
        stock = Ticker(stock_symbol)
        fundamentals = stock.financial_data.get(stock_symbol, {})
        debt_to_equity = fundamentals.get("debtToEquity", None) or stock.key_stats.get(stock_symbol, {}).get("debtToEquity", None)
        eps_growth = fundamentals.get("earningsGrowth", None)
        pe_ratio = fundamentals.get("trailingPE", None) or stock.summary_detail.get(stock_symbol, {}).get("trailingPE", None)
        roe = fundamentals.get("returnOnEquity", None)
        revenue_growth = fundamentals.get("revenueGrowth", None)

        def classify(value, good, neutral, bad):
            if value is None:
                return "Neutral"
            if value >= good:
                return "Good"
            elif value >= neutral:
                return "Neutral"
            else:
                return "Bad"

        analysis = {
            "Debt-to-Equity": classify(debt_to_equity, 0.5, 1.0, 2.0),
            "EPS Growth": classify(eps_growth, 0.10, 0.05, 0.00),
            "P/E Ratio": classify(pe_ratio, 10, 20, 40),
            "ROE": classify(roe, 0.15, 0.10, 0.05),
            "Revenue Growth": classify(revenue_growth, 0.10, 0.05, 0.00)
        }

        values = list(analysis.values())
        good_count = values.count("Good")
        bad_count = values.count("Bad")

        overall = "Good" if good_count >= 3 else "Bad" if bad_count >= 3 else "Neutral"
        analysis["Overall Classification"] = overall
        return analysis
    except Exception as e:
        print(f"Error fetching fundamental data: {e}")
        return {
            "Debt-to-Equity": "Neutral",
            "EPS Growth": "Neutral",
            "P/E Ratio": "Neutral",
            "ROE": "Neutral",
            "Revenue Growth": "Neutral",
            "Overall Classification": "Neutral"
        }

@sentiment_bp.route('/news', methods=['GET'])
def get_stock_news():
    stock_symbol = request.args.get('symbol', 'RELIANCE.NS')
    print(f"Fetching news & fundamentals for {stock_symbol}...")

    news = get_google_news(stock_symbol)
    if not news:
        return jsonify({"error": "No news found for this stock"}), 404
    analyzed_news, overall_sentiment = analyze_sentiment(news)
    fundamentals = fetch_fundamental_analysis(stock_symbol)

    response = {
        "stock": stock_symbol,
        "overall_sentiment": overall_sentiment,
        "fundamental_analysis": fundamentals,
        "articles": analyzed_news
    }

    return jsonify(response)
