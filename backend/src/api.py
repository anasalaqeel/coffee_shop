import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

## ROUTES

@app.route("/drinks")
def get_all_drinks():
    get_drinks = Drink.query.all()
    # print(get_drinks)
    return jsonify({'success': True, 'drinks': [drink.short() for drink in get_drinks]})


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    get_drinks = Drink.query.all()
    # print(get_drinks)
    return jsonify({'success': True, 'drinks': [drink.long() for drink in get_drinks]}), 200


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    error = False
    title = request.get_json()['title']
    recipe = request.get_json()['recipe']
    # print(title)
    try:
        added_drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )
        Drink.insert(added_drink)
    except:
        erroe = True
        print(sys.exc_info())
    finally:
        if error:
            abort (422)
        else:
            return jsonify({'success': True, 'drinks': [added_drink.long()]})


@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    error = False
    title = request.get_json()['title']
    recipe = request.get_json()['recipe']
    get_drink = Drink.query.filter_by(id=drink_id).first()
    try:
        get_drink.title=title
        get_drink.recipe=json.dumps(recipe)
        get_drink.update()
    except:
        erroe = True
        print(sys.exc_info())
    finally:
        if error:
            abort (404)
        else:
            # print(get_drink)
            return jsonify({'success': True, 'drinks': [get_drink.long()]})


@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    error = False
    get_drink = Drink.query.filter_by(id=drink_id).first()
    try:
        Drink.delete(get_drink)
    except:
        erroe = True
        print(sys.exc_info())
    finally:
        if error:
            abort (404)
        else:
            # print(get_drink)
            return jsonify({'success': True, 'delete': drink_id})


## Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Unauthorized"
                    }), 401

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
    
@app.errorhandler(500)
def server_error(error):
  return jsonify({
    "success": False,
    "error": 500,
    "message": "Internal Server Error"
  }), 500