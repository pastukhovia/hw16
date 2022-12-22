from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from utils import read_from_json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Модели
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    age = db.Column(db.Integer)
    email = db.Column(db.Text)
    role = db.Column(db.Text)
    phone = db.Column(db.Text)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    start_date = db.Column(db.Text)
    end_date = db.Column(db.Text)
    address = db.Column(db.Text)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship("User", primaryjoin=customer_id==User.id)


class Offer(db.Model):
    __tablename__ = "offers"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    orders = db.relationship("Order")
    users = db.relationship("User")

# Создание базы данных и заполнение таблиц данными из json файлов
with app.app_context():
    db.drop_all()
    db.create_all()

    with db.session.begin():
        users = read_from_json('./json_data/users_data.json')
        users_list = []
        for user in users:
            users_list.append(User(
                id=user['id'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                age=user['age'],
                email=user['email'],
                role=user['role'],
                phone=user['phone']
            ))
        db.session.add_all(users_list)
        db.session.commit()

    with db.session.begin():
        orders = read_from_json('./json_data/orders_data.json')
        orders_list = []
        for order in orders:
            orders_list.append(Order(
                id=order['id'],
                name=order['name'],
                description=order['description'],
                start_date=order['start_date'],
                end_date=order['end_date'],
                address=order['address'],
                price=order['price'],
                customer_id=order['customer_id'],
                executor_id=order['executor_id']
            ))
        db.session.add_all(orders_list)
        db.session.commit()

    with db.session.begin():
        offers = read_from_json('./json_data/offers_data.json')
        offers_list = []
        for offer in offers:
            offers_list.append(Offer(
                id=offer['id'],
                order_id=offer['order_id'],
                executor_id=offer['executor_id']
            ))
        db.session.add_all(offers_list)
        db.session.commit()


# эндпоинты. Добавление и обновление записей происходит без ввода id, чтобы избежать их повторения
@app.route('/users', methods=['GET', 'POST'])
def all_users_page():
    if request.method == 'GET':
        users_query = User.query.all()
        result = []

        for user in users_query:
            result.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone
            })

        return jsonify(result)
    elif request.method == 'POST':
        user_data = request.get_json()
        with db.session.begin():
            new_user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                age=user_data['age'],
                email=user_data['email'],
                role=user_data['role'],
                phone=user_data['phone']
            )
            db.session.add(new_user)
            db.session.commit()

        return 'New user added'


@app.route('/users/<id>', methods=['GET', 'PUT', 'DELETE'])
def user_by_id_page(id):
    if request.method == 'GET':
        user = User.query.get(id)
        if user:
            return jsonify({
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'age': user.age,
                    'email': user.email,
                    'role': user.role,
                    'phone': user.phone
                })
        else:
            return f'User {id} not found'
    elif request.method == 'PUT':
        with db.session.begin():
            searched_user = User.query.get(id)
            new_data = request.get_json()

            searched_user.first_name = new_data['first_name']
            searched_user.first_name = new_data['first_name']
            searched_user.last_name = new_data['last_name']
            searched_user.age = new_data['age']
            searched_user.email = new_data['email']
            searched_user.role = new_data['role']
            searched_user.phone = new_data['phone']

            db.session.add(searched_user)
            db.session.commit()

        return f'User {id} updated'
    elif request.method == 'DELETE':
        with db.session.begin():
            searched_user = User.query.get(id)
            db.session.delete(searched_user)
            db.session.commit()

        return f'User {id} deleted'


@app.route('/orders', methods=['GET', 'POST'])
def all_orders_page():
    if request.method == 'GET':
        orders_query = Order.query.all()
        result = []

        for order in orders_query:
            result.append({
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'address': order.address,
                'price': order.price,
                'customer_id': order.customer_id,
                'executor_id': order.executor_id
            })

        return jsonify(result)
    elif request.method == 'POST':
        order_data = request.get_json()
        with db.session.begin():
            new_order = Order(
                name=order_data['name'],
                description=order_data['description'],
                start_date=order_data['start_date'],
                end_date=order_data['end_date'],
                address=order_data['address'],
                price=order_data['price'],
                customer_id=order_data['customer_id'],
                executor_id=order_data['executor_id']
            )
            db.session.add(new_order)
            db.session.commit()

        return 'New order added'


@app.route('/orders/<id>', methods=['GET', 'PUT', 'DELETE'])
def order_by_id_page(id):
    if request.method == 'GET':
        order = Order.query.get(id)
        if order:
            return jsonify({
                    'id': order.id,
                    'name': order.name,
                    'description': order.description,
                    'start_date': order.start_date,
                    'end_date': order.end_date,
                    'address': order.address,
                    'price': order.price,
                    'customer_id': order.customer_id,
                    'executor_id': order.executor_id
                })
        else:
            return f'Order {id} not found'
    elif request.method == 'PUT':
        with db.session.begin():
            searched_order = Order.query.get(id)
            new_data = request.get_json()

            searched_order.name = new_data['name']
            searched_order.description = new_data['description']
            searched_order.start_date = new_data['start_date']
            searched_order.end_date = new_data['end_date']
            searched_order.address = new_data['address']
            searched_order.price = new_data['price']
            searched_order.customer_id = new_data['customer_id']
            searched_order.executor_id = new_data['executor_id']

            db.session.add(searched_order)
            db.session.commit()

        return f'Order {id} updated'
    elif request.method == 'DELETE':
        with db.session.begin():
            searched_order = Order.query.get(id)
            db.session.delete(searched_order)
            db.session.commit()

        return f'Order {id} deleted'


@app.route('/offers', methods=['GET', 'POST'])
def all_offers_page():
    if request.method == 'GET':
        offers_query = Offer.query.all()
        result = []

        for offer in offers_query:
            result.append({
                'id': offer.id,
                'order_id': offer.order_id,
                'executor_id': offer.executor_id
            })

        return jsonify(result)
    elif request.method == 'POST':
        offer_data = request.get_json()
        with db.session.begin():
            new_offer = Offer(
                order_id=offer_data['order_id'],
                executor_id=offer_data['executor_id']
            )
            db.session.add(new_offer)
            db.session.commit()

        return 'New offer added'


@app.route('/offers/<id>', methods=['GET', 'PUT', 'DELETE'])
def offer_by_id_page(id):
    if request.method == 'GET':
        offer = Offer.query.get(id)
        if offer:
            return jsonify({
                    'id': offer.id,
                    'order_id': offer.order_id,
                    'executor_id': offer.executor_id
                })
        else:
            return f'Offer {id} not found'
    elif request.method == 'PUT':
        with db.session.begin():
            searched_offer = Offer.query.get(id)
            new_data = request.get_json()

            searched_offer.order_id = new_data['order_id']
            searched_offer.executor_id = new_data['executor_id']

            db.session.add(searched_offer)
            db.session.commit()

        return f'Offer {id} updated'
    elif request.method == 'DELETE':
        with db.session.begin():
            searched_offer = Offer.query.get(id)
            db.session.delete(searched_offer)
            db.session.commit()

        return f'Offer {id} deleted'


if __name__ == '__main__':
    app.run(debug=True)
