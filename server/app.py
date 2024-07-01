#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(include_pizzas=False) for restaurant in restaurants]), 200
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return jsonify(restaurant.to_dict()), 200
        else:
            return jsonify({"error": "Restaurant not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        else:
            return jsonify({"error": "Restaurant not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas]), 200
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    try:
        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5555)    
