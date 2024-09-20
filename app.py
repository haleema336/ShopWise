from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from math import ceil
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)

IST = pytz.timezone('Asia/Kolkata')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))

@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.args.get('search', '')
    category = request.args.get('category', '')

    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    products_query = Product.query
    if search_query:
        products_query = products_query.filter(Product.name.contains(search_query))
    
    if category:
        products_query = products_query.filter(Product.category == category)

    total_products = products_query.count()
    total_pages = ceil(total_products / per_page)

    products = products_query.order_by(Product.created_at.desc()).offset(offset).limit(per_page).all()

    search_results = bool(search_query and total_products > 0)

    return render_template('index.html', products=products, total_pages=total_pages, current_page=page, search_results=search_results)

@app.route('/add', methods=['POST'])
def add_product():
    product_name = request.form['name']
    product_price = request.form['price']
    product_category = request.form['category']
    
    new_product = Product(
        name=product_name, 
        price=product_price, 
        category=product_category
    )
    try:
        db.session.add(new_product)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue adding your product'

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.category = request.form['category']
        db.session.commit()
        return redirect('/')
    return render_template('edit.html', product=product)

@app.route('/delete/<int:id>')
def delete(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue deleting your product'

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
