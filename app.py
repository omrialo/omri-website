from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime
import json
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store tracked stocks in memory (in a real app, this would be in a database)
tracked_stocks = {}

@app.route('/')
def home():
    logger.info('Rendering home page')
    return render_template('index.html', stocks=tracked_stocks)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    try:
        logger.info('=== Starting add_stock request ===')
        logger.info(f'Request headers: {dict(request.headers)}')
        logger.info(f'Request content type: {request.content_type}')
        logger.info(f'Raw request data: {request.get_data(as_text=True)}')
        
        if not request.is_json:
            logger.error('Request is not JSON')
            return jsonify({'success': False, 'error': 'Request must be JSON'})
            
        data = request.get_json()
        logger.info(f'Parsed JSON data: {data}')
        
        if not data:
            logger.error('No data provided in request')
            return jsonify({'success': False, 'error': 'No data provided'})
            
        ticker = data.get('ticker', '').upper()
        if not ticker:
            logger.error('No ticker provided')
            return jsonify({'success': False, 'error': 'Ticker symbol is required'})
        
        logger.info(f'Fetching data for ticker: {ticker}')
        try:
            # Download the stock data
            df = yf.download(ticker, period='1d', progress=False)
            
            if df.empty:
                logger.error(f'No data found for ticker: {ticker}')
                return jsonify({'success': False, 'error': f'Could not find stock with ticker {ticker}'})
            
            # Calculate the change percentage
            current_price = df['Close'].iloc[-1]
            open_price = df['Open'].iloc[0]
            change_percent = ((current_price - open_price) / open_price) * 100
            
            # Get basic stock information
            tracked_stocks[ticker] = {
                'name': ticker,
                'last_price': current_price,
                'change': change_percent,
                'volume': df['Volume'].iloc[-1],
                'market_cap': 'N/A',
                'pe_ratio': 'N/A',
                'dividend_yield': 'N/A',
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f'Successfully added stock: {ticker}')
            return jsonify({'success': True, 'stock': tracked_stocks[ticker]})
        except Exception as e:
            logger.error(f'Error fetching stock data: {str(e)}')
            logger.error(f'Traceback: {traceback.format_exc()}')
            return jsonify({
                'success': False, 
                'error': f'Error fetching data for {ticker}. Please try again later or check if the ticker symbol is correct.'
            })
            
    except json.JSONDecodeError as e:
        logger.error(f'JSON decode error: {str(e)}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f'Error adding stock: {str(e)}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    try:
        logger.info('Received remove_stock request')
        data = request.get_json()
        logger.info(f'Request data: {data}')
        
        if not data:
            logger.error('No data provided in request')
            return jsonify({'success': False, 'error': 'No data provided'})
            
        ticker = data.get('ticker', '').upper()
        if not ticker:
            logger.error('No ticker provided')
            return jsonify({'success': False, 'error': 'Ticker symbol is required'})
        
        if ticker in tracked_stocks:
            del tracked_stocks[ticker]
            logger.info(f'Successfully removed stock: {ticker}')
            return jsonify({'success': True})
        logger.error(f'Stock not found: {ticker}')
        return jsonify({'success': False, 'error': 'Stock not found'})
    except Exception as e:
        logger.error(f'Error removing stock: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_stocks', methods=['GET'])
def update_stocks():
    try:
        logger.info('Updating all stocks')
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
                logger.info(f'Updated stock: {ticker}')
            except Exception as e:
                logger.error(f'Error updating stock {ticker}: {str(e)}')
        
        return jsonify({'success': True, 'stocks': tracked_stocks})
    except Exception as e:
        logger.error(f'Error updating stocks: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 