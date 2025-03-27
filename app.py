from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Store tracked stocks in memory (in a real app, this would be in a database)
tracked_stocks = {}

@app.route('/')
def home():
    return render_template('index.html', stocks=tracked_stocks)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    data = request.json
    ticker = data.get('ticker', '').upper()
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get basic stock information
        tracked_stocks[ticker] = {
            'name': info.get('longName', ticker),
            'last_price': info.get('regularMarketPrice', 'N/A'),
            'change': info.get('regularMarketChangePercent', 'N/A'),
            'volume': info.get('regularMarketVolume', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('forwardPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({'success': True, 'stock': tracked_stocks[ticker]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    data = request.json
    ticker = data.get('ticker', '').upper()
    
    if ticker in tracked_stocks:
        del tracked_stocks[ticker]
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Stock not found'})

@app.route('/update_stocks', methods=['GET'])
def update_stocks():
    for ticker in tracked_stocks:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            tracked_stocks[ticker].update({
                'last_price': info.get('regularMarketPrice', 'N/A'),
                'change': info.get('regularMarketChangePercent', 'N/A'),
                'volume': info.get('regularMarketVolume', 'N/A'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            print(f"Error updating {ticker}: {str(e)}")
    
    return jsonify({'success': True, 'stocks': tracked_stocks})

if __name__ == '__main__':
    app.run(debug=True) 