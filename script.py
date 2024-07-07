import pandas as pd
import sqlalchemy as db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Database connection setup
DATABASE_URI = 'sqlite:///ecommerce.db'
engine = db.create_engine(DATABASE_URI)
Base = declarative_base()

# Product table definition
class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    category = Column(String)
    price = Column(Float)
    quantity_sold = Column(Integer)
    rating = Column(Float)
    review_count = Column(Integer)

# Users table definition
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# Create tables
Base.metadata.create_all(engine)

# Session setup
Session = sessionmaker(bind=engine)
session = Session()

# Load data from CSV
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['price'] = df['price'].fillna(df['price'].median())
    df['quantity_sold'] = df['quantity_sold'].fillna(df['quantity_sold'].median())
    df['rating'] = df.groupby('category')['rating'].transform(lambda x: x.fillna(x.mean()))
    df.to_sql('products', con=engine, if_exists='append', index=False)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ecom@#1234'

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    try:
        session.add(new_user)
        session.commit()
        return jsonify({'message': 'User created successfully!'})
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'message': 'User creation failed!', 'error': str(e)})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = session.query(User).filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials!'})

@app.route('/summary', methods=['GET'])
def summary():
    query = """
    SELECT
        category,
        SUM(price * quantity_sold) AS total_revenue,
        MAX(quantity_sold) AS top_product_quantity_sold
    FROM
        products
    GROUP BY
        category
    """
    result = engine.execute(query).fetchall()
    summary_data = []
    for row in result:
        category, total_revenue, top_product_quantity_sold = row
        top_product = engine.execute(f"SELECT product_name FROM products WHERE category = '{category}' AND quantity_sold = {top_product_quantity_sold}").fetchone()[0]
        summary_data.append({
            'category': category,
            'total_revenue': total_revenue,
            'top_product': top_product,
            'top_product_quantity_sold': top_product_quantity_sold
        })
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('summary_report.csv', index=False)
    return jsonify(summary_data)

if __name__ == '__main__':
    load_data('products.csv')
    app.run(debug=True)
