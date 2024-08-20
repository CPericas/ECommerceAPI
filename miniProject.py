from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:%24E%40kster1@localhost/e_commerce_db"
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=True)
    accounts = db.relationship('CustomerAccount', backref='customer', lazy=True)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

class CustomerAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

class CustomerAccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CustomerAccount

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route('/')
def home():
    return jsonify(message="Welcome to the E-Commerce API!")

@app.route('/customers', methods=['POST'])
def create_customer():
    name = request.json['name']
    email = request.json['email']
    phone = request.json.get('phone')

    new_customer = Customer(name=name, email=email, phone=phone)
    try:
        db.session.add(new_customer)
        db.session.commit()
    except IntegrityError:
        return jsonify(message="Customer with this email or phone already exists"), 409

    return customer_schema.jsonify(new_customer), 201

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    
    customer.name = request.json.get('name', customer.name)
    customer.email = request.json.get('email', customer.email)
    customer.phone = request.json.get('phone', customer.phone)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="Customer with this email or phone already exists"), 409

    return customer_schema.jsonify(customer)

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify(message="Customer deleted successfully"), 200

@app.route('/customeraccounts', methods=['POST'])
def create_customer_account():
    username = request.json['username']
    password = request.json['password']
    customer_id = request.json['customer_id']

    new_customer_account = CustomerAccount(username=username, password=password, customer_id=customer_id)
    try:
        db.session.add(new_customer_account)
        db.session.commit()
    except IntegrityError:
        return jsonify(message="CustomerAccount with this username already exists"), 409

    return customer_account_schema.jsonify(new_customer_account), 201

@app.route('/customeraccounts/<int:id>', methods=['GET'])
def get_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    return customer_account_schema.jsonify(customer_account)

@app.route('/customeraccounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)

    customer_account.username = request.json.get('username', customer_account.username)
    customer_account.password = request.json.get('password', customer_account.password)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="CustomerAccount with this username already exists"), 409

    return customer_account_schema.jsonify(customer_account)

@app.route('/customeraccounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify(message="CustomerAccount deleted successfully"), 200

@app.route('/products', methods=['POST'])
def create_product():
    name = request.json['name']
    description = request.json.get('description')
    price = request.json['price']
    stock_quantity = request.json['stock_quantity']
    
    new_product = Products(name=name, description=description, price=price, stock_quantity=stock_quantity)
    try:
        db.session.add(new_product)
        db.session.commit()
    except IntegrityError:
        return jsonify(message="Product with this name already exists"), 409

    return product_schema.jsonify(new_product), 201

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Products.query.get_or_404(id)
    return product_schema.jsonify(product)

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Products.query.get_or_404(id)
    
    product.name = request.json.get('name', product.name)
    product.description = request.json.get('description', product.description)
    product.price = request.json.get('price', product.price)
    product.stock_quantity = request.json.get('stock_quantity', product.stock_quantity)
    
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="Error updating product"), 400

    return product_schema.jsonify(product)

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Products.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify(message="Product deleted successfully"), 200

@app.route('/products', methods=['GET'])
def list_products():
    products = Products.query.all()
    return products_schema.jsonify(products)

@app.route('/products/stock', methods=['GET'])
def view_stock_levels():
    products = Products.query.all()
    return products_schema.jsonify(products)

@app.route('/products/restock', methods=['POST'])
def restock_product():
    product_id = request.json['product_id']
    restock_amount = request.json['restock_amount']
    
    product = Products.query.get_or_404(product_id)
    product.stock_quantity += restock_amount
    
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="Error restocking product"), 400

    return product_schema.jsonify(product)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

