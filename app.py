from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from utils import dictionary_users, dictionary_orders, dictionary_offers
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_AS_ASCII"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)   #попытка сделать чуть по другому
    phone = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    address = db.Column(db.String)
    price = db.Column(db.Float)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.executor_id
        }


class Offer(db.Model):
    __tablename__ = "offers"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id
        }


db.create_all()

for i in dictionary_users():
    db.session.add(
        User(id=i['id'],
             first_name=i['first_name'],
             last_name=i['last_name'],
             age=i['age'],
             email=i['email'],
             role=i['role'],
             phone=i['phone']))

for i in dictionary_orders():
    db.session.add(
        Order(id=i['id'],
              name=i['name'],
              description=i['description'],
              start_date=i['start_date'],
              end_date=i['end_date'],
              address=i['address'],
              price=i['price'],
              customer_id=i['customer_id'],
              executor_id=i['executor_id']))

db.session.add_all(
    [Offer(id=offer['id'],
           order_id=offer['order_id'],
           executor_id=offer['executor_id']) for offer in dictionary_offers()])

db.session.commit()

@app.route("/")
def get_start():
    """Стартовая страничка"""
    return f"Привет, я работаю :)"

@app.route("/users", methods=['GET', 'POST'])
def get_all_users():
    """Функция получает всех пользователей."""
    if request.method == 'GET':
        result = []
        users = User.query.all()
        for user in users:
            result.append(user.to_dict())
        return jsonify(result)
    if request.method == 'POST':
        user = json.loads(request.data)
        new_user_obj = User(id=user['id'],
                            first_name=user['first_name'],
                            last_name=user['last_name'],
                            age=user['age'],
                            email=user['email'],
                            role=user['role'],
                            phone=user['phone'])
        db.session.add(new_user_obj)
        db.session.commit()
        db.session.close()
        return "Пользователь внесен", 200


@app.route("/users/<int:us>", methods=['GET', 'PUT', 'DELETE'])
def get_one_user(us):
    """Функция одного одинешеньку пользователя"""
    if request.method == 'GET':
        user = User.query.get(us)
        if user is None:
            return "Нет такого пользователя"
        else:
            return jsonify(user.to_dict())
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        user = db.session.query(User).get(us)
        if user is None:
            return "Пользователь не найден", 404
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.add(user)
        db.session.commit()
        return f"Объект с id {us} успешно изменен", 200
    elif request.method == 'DELETE':
        user = db.session.query(User).get(us)
        if user is None:
            return "Нет такого пользователя", 404
        db.session.delete(user)
        db.session.commit()
        db.session.close()
        return f"Пользователь с id {us} удален", 200

@app.route("/orders", methods=['GET', 'POST'])
def get_orders():
    """Функция выводит все заказы."""
    if request.method == 'GET':
        result = []
        orders = Order.query.all()
        for order in orders:
            result.append(order.to_dict())
        return jsonify(result)
    if request.method == 'POST':
        order = json.loads(request.data)
        new_order_obj = Order(id=order['id'],
                              name=order['name'],
                              description=order['description'],
                              start_date=order['start_date'],
                              end_date=order['end_date'],
                              address=order['address'],
                              price=order['price'],
                              customer_id=order['customer_id'],
                              executor_id=order['executor_id'])
        db.session.add(new_order_obj)
        db.session.commit()
        db.session.close()
        return "Заказ создан", 200

@app.route("/orders/<int:or_id>", methods=['GET', 'PUT', 'DELETE'])
def get_one_order(or_id):
    if request.method == 'GET':
        order = Order.query.get(or_id)
        if order is None:
            return "Нет заказа с таким номерком"
        else:
            return jsonify(order.to_dict())
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        order = db.session.query(Order).get(or_id)
        if order is None:
            return "Заказ не найден", 404
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.address = order_data['address']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']

        db.session.add(order)
        db.session.commit()
        db.session.close()
        return f"Заказ {or_id} изменен", 200

    elif request.method == 'DELETE':
        order = db.session.query(Order).get(or_id)
        if order is None:
            return "Заказ не обнаружен"
        db.session.delete(order)
        db.session.commit()
        db.session.close()
        return f"Заказ {or_id} удален", 200


@app.route("/offers", methods=['GET', 'POST'])
def get_offers():
    """Функция выводит все предложния"""
    if request.method == 'GET':
        result = []
        offers = Offer.query.all()
        for offer in offers:
            result.append(offer.to_dict())
        return jsonify(result)
    if request.method == 'POST':
        offer = json.loads(request.data)
        new_offer_obj = Offer(id=offer['id'],
                              order_id=offer['order_id'],
                              executor_id=offer['executor_id'])
        db.session.add(new_offer_obj)
        db.session.commit()
        db.session.close()
        return "Предложение создано", 200

@app.route("/offers/<int:of_id>", methods=['GET', 'PUT', 'DELETE'])
def get_one_offer(of_id):
    if request.method == 'GET':
        offer = Offer.query.get(of_id)
        if offer is None:
            return "Нет предложений с таким номерком"
        else:
            return jsonify(offer.to_dict())
    elif request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer = db.session.query(Offer).get(of_id)
        if offer is None:
            return "Предложение не найдено", 404
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']

        db.session.add(offer)
        db.session.commit()
        db.session.close()
        return f"Предложение {of_id} изменено", 200

    elif request.method == 'DELETE':
        offer = db.session.query(Offer).get(of_id)
        if offer is None:
            return "Предложение не обнаружено"
        db.session.delete(offer)
        db.session.commit()
        db.session.close()
        return f"Предложение {of_id} удалено", 200


if __name__ == "__main__":
    app.run(port=890, debug=True)
