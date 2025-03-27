from flask import Flask, render_template, request, jsonify, session
from finnhub import client as Finnhub
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from models import db, User, UserStock

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Database configuration
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'stocks.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize Finnhub client
finnhub_client = Finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))

def init_db():
    with app.app_context():
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Create all tables
        db.create_all()
        logger.info(f"Database initialized at: {db_path}")

# Initialize database tables
init_db()

def get_or_create_user(name):
    user = User.query.filter_by(name=name).first()
    if not user:
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
    return user

@app.route('/')
def home():
    logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'success': False, 'error': 'Name is required'})
    
    user = get_or_create_user(name)
    session['user_id'] = user.id
    session['user_name'] = user.name
    
    # Get user's stocks
    stocks = {}
    for user_stock in user.stocks:
        stocks[user_stock.ticker] = {
            'name': user_stock.name,
            'last_price': user_stock.last_price,
            'change': user_stock.change,
            'market_cap': user_stock.market_cap,
            'volume': user_stock.volume,
            'pe_ratio': user_stock.pe_ratio,
            'dividend_yield': user_stock.dividend_yield
        }
    
    return jsonify({
        'success': True,
        'user': {'name': user.name},
        'stocks': stocks
    })

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/add_stock', methods=['POST'])
def add_stock():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please login first'})
    
    data = request.get_json()
    ticker = data.get('ticker')
    
    if not ticker:
        return jsonify({'success': False, 'error': 'Ticker is required'})
    
    try:
        # Get stock data from Finnhub
        quote = finnhub_client.quote(ticker)
        profile = finnhub_client.company_profile2(symbol=ticker)
        
        if not quote or not profile:
            return jsonify({'success': False, 'error': 'No data found for this ticker'})
        
        # Calculate change percentage
        change = ((quote['c'] - quote['pc']) / quote['pc']) * 100
        
        # Create stock data
        stock_data = {
            'name': profile.get('name', ticker),
            'last_price': quote['c'],
            'change': change,
            'market_cap': profile.get('marketCapitalization', 0),
            'volume': quote['v'],
            'pe_ratio': profile.get('pe', 0),
            'dividend_yield': profile.get('dividendYield', 0)
        }
        
        # Save to database
        user_stock = UserStock(
            user_id=session['user_id'],
            ticker=ticker,
            **stock_data
        )
        db.session.add(user_stock)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'stock': stock_data
        })
        
    except Exception as e:
        logger.error(f"Error adding stock: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please login first'})
    
    data = request.get_json()
    ticker = data.get('ticker')
    
    if not ticker:
        return jsonify({'success': False, 'error': 'Ticker is required'})
    
    try:
        # Remove from database
        UserStock.query.filter_by(
            user_id=session['user_id'],
            ticker=ticker
        ).delete()
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error removing stock: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_stocks')
def update_stocks():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please login first'})
    
    try:
        user = User.query.get(session['user_id'])
        stocks = {}
        
        for user_stock in user.stocks:
            # Get updated data from Finnhub
            quote = finnhub_client.quote(user_stock.ticker)
            profile = finnhub_client.company_profile2(symbol=user_stock.ticker)
            
            if quote and profile:
                # Calculate change percentage
                change = ((quote['c'] - quote['pc']) / quote['pc']) * 100
                
                # Update database
                user_stock.last_price = quote['c']
                user_stock.change = change
                user_stock.market_cap = profile.get('marketCapitalization', 0)
                user_stock.volume = quote['v']
                user_stock.pe_ratio = profile.get('pe', 0)
                user_stock.dividend_yield = profile.get('dividendYield', 0)
                
                # Add to response
                stocks[user_stock.ticker] = {
                    'name': user_stock.name,
                    'last_price': user_stock.last_price,
                    'change': user_stock.change,
                    'market_cap': user_stock.market_cap,
                    'volume': user_stock.volume,
                    'pe_ratio': user_stock.pe_ratio,
                    'dividend_yield': user_stock.dividend_yield
                }
        
        db.session.commit()
        return jsonify({'success': True, 'stocks': stocks})
        
    except Exception as e:
        logger.error(f"Error updating stocks: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 