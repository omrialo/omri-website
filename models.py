from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stocks = db.relationship('UserStock', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

class UserStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_price = db.Column(db.Float)
    change = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    volume = db.Column(db.Integer)
    pe_ratio = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f'<UserStock {self.ticker} for user {self.user_id}>' 