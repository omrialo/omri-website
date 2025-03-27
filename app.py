from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime
import json

app = Flask(__name__)

# Store tracked stocks in memory (in a real app, this would be in a database)
tracked_stocks = {}

@app.route('/')
def home():
    return render_template('index.html', stocks=tracked_stocks)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
            
        ticker = data.get('ticker', '').upper()
        if not ticker:
            return jsonify({'success': False, 'error': 'Ticker symbol is required'})
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info:
            return jsonify({'success': False, 'error': f'Could not find stock with ticker {ticker}'})
        
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
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
            
        ticker = data.get('ticker', '').upper()
        if not ticker:
            return jsonify({'success': False, 'error': 'Ticker symbol is required'})
        
        if ticker in tracked_stocks:
            del tracked_stocks[ticker]
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Stock not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_stocks', methods=['GET'])
def update_stocks():
    try:
        for ticker in tracked_stocks:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            tracked_stocks[ticker].update({
                'last_price': info.get('regularMarketPrice', 'N/A'),
                'change': info.get('regularMarketChangePercent', 'N/A'),
                'volume': info.get('regularMarketVolume', 'N/A'),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'stocks': tracked_stocks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 