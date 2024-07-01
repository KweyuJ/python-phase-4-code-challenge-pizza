from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', cascade='all, delete-orphan')
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    serialize_rules = ('-restaurant_pizzas.restaurant', '-pizzas.restaurants')

    def to_dict(self, include_pizzas=True):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
        }
        if include_pizzas:
            data['restaurant_pizzas'] = [{'id': rp.id, 'price': rp.price, 'pizza_id': rp.pizza_id} for rp in self.restaurant_pizzas]
        return data

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza', cascade='all, delete-orphan')
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurants.pizzas')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'pizza': {'id': self.pizza.id, 'name': self.pizza.name, 'ingredients': self.pizza.ingredients},
            'restaurant': {'id': self.restaurant.id, 'name': self.restaurant.name, 'address': self.restaurant.address}
        }

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
