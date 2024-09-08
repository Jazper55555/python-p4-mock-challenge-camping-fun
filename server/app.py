#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return 'API Home Page'


class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        response = []
        for activity in activities:
            activity_data = {
                'id': activity.id,
                'name': activity.name,
                'difficulty': activity.difficulty
            }
            response.append(activity_data)

        return make_response(jsonify(response), 200)
    
class Activity_by_id(Resource):
    def delete(self, id):
        try:
            activity = Activity.query.filter(Activity.id == id).first()

            db.session.delete(activity)
            db.session.commit()

            return make_response('', 204)
        
        except:
            return make_response({'error': 'Activity not found'}, 404)

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        response = []
        for camper in campers:
            camper_data = {
                'id': camper.id,
                'name': camper.name,
                'age': camper.age
            }
            response.append(camper_data)

        return make_response(jsonify(response), 200)
    
    def post(self):
        try:
            new_camper = Camper(
                name = request.get_json()['name'],
                age = request.get_json()['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            
            response = {
                'id': new_camper.id,
                'name': new_camper.name,
                'age': new_camper.age
            }

            return make_response(jsonify(response), 200)
        
        except:
            db.session.rollback()
            return make_response(jsonify({'errors': ['validation errors']}), 400)


class Camper_by_id(Resource):
    def get(self, id):
        try:
            camper = Camper.query.filter(Camper.id == id).first()
            return make_response(jsonify(camper.to_dict()), 200)
        
        except:
            return make_response(jsonify({'error': 'Camper not found'}), 404)
        
    def patch(self, id):
        try:
            camper = Camper.query.filter(Camper.id == id).first()

            if camper:
                for attr in request.get_json():
                    setattr(camper, attr, request.get_json()[attr])

                db.session.add(camper)
                db.session.commit()

                response = {
                    'id': camper.id,
                    'name': camper.name,
                    'age': camper.age
                }

                return make_response(response, 202)
            
            return make_response({'error': 'Camper not found'}, 404)

        except:
            return make_response({'errors': ['validation errors']}, 400)
        

class Signups(Resource):
    def post(self):
        try:
            new_signup = Signup(
                camper = Camper.query.get(request.get_json().get('camper_id')),
                activity = Activity.query.get(request.get_json().get('activity_id')),
                time = request.get_json().get('time')
            )

            db.session.add(new_signup)
            db.session.commit()

            response = {
                'id': new_signup.id,
                'camper_id': new_signup.camper_id,
                'activity_id': new_signup.activity_id,
                'time': new_signup.time,
                'activity': {
                    'difficulty': new_signup.activity.difficulty,
                    'id': new_signup.activity.id,
                    'name': new_signup.activity.name,
                },
                'camper': {
                    'age': new_signup.camper.age,
                    'id': new_signup.camper.id,
                    'name': new_signup.camper.name,
                }
            }

            return make_response(jsonify(response), 200)
        
        except:
            return make_response({'errors': ['validation errors']}, 400)
    
api.add_resource(Activities, '/activities')
api.add_resource(Activity_by_id, '/activities/<int:id>')    
api.add_resource(Campers, '/campers')
api.add_resource(Camper_by_id, '/campers/<int:id>')
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
