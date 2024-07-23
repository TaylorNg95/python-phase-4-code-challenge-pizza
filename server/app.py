#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True) # change to render as batch

db.init_app(app)

api = Api(app)

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(rules=['-restaurant_pizzas',]) for restaurant in restaurants], 200

api.add_resource(RestaurantsResource, '/restaurants', endpoint='restaurants')

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            return restaurant.to_dict(), 200
        else:
            return {'error': 'Restaurant not found'}, 404
        
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        else:
            return {'error': 'Restaurant not found'}, 404

api.add_resource(RestaurantResource, '/restaurants/<int:id>', endpoint='restaurant')

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(rules=['-restaurant_pizzas',]) for pizza in pizzas], 200

api.add_resource(PizzasResource, '/pizzas', endpoint='pizzas')

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')
        try:
            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()
            return restaurant_pizza.to_dict(), 201
        except:
            return {'errors': ['validation errors']}, 400

api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas', endpoint='restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
