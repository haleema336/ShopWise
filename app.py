from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from math import ceil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    category = db.Column(db.String(50)) 


@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'name')
    category = request.args.get('category', '')

    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    products_query = Product.query.filter(Product.name.contains(search_query))
    if category:
        products_query = products_query.filter(Product.category == category)

    total_products = products_query.count()
    total_pages = ceil(total_products / per_page)

    if sort_by == 'price':
        products = products_query.order_by(Product.price).offset(offset).limit(per_page).all()
    else:
        products = products_query.order_by(Product.name).offset(offset).limit(per_page).all()

    return render_template('index.html', products=products, total_pages=total_pages, current_page=page)

@app.route('/add', methods=['POST'])
def add_product():
    product_name = request.form['name']
    product_price = request.form['price']
    product_category = request.form['category']
    
    new_product = Product(name=product_name, price=product_price, category=product_category)
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
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your product'
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

