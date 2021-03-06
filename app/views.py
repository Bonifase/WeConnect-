from flask import request, jsonify, make_response, session, logging
import json, re
from flask_login import LoginManager
from functools import wraps

from app import app

from .models import User
from .models import Business
from .models import Review

from app.helpers import clean_data


business_reviews = []

@app.route('/')
def index():
    return jsonify("Welcome To WeConnect")


# Endpoint to Register user and ssaving the details in a list called users


@app.route('/api/v1/auth/register',  methods=['POST'])
def register_user():
    
        data = request.get_json()
        cleaned_data = clean_data(data)
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if username is None:
            return make_response(jsonify({"error": "Missing key"}), 500)

        # check if the user details already in the list, otherwise add the details in the list
        available_emails = [user.email for user in User.users]
        if email in available_emails:
            return make_response(jsonify({"message": "Email already registered, singup with a different Email"}), 409)
        else:
            try:
                user = User.register_user(username, email, password)
            except AssertionError as err:
                return make_response(jsonify({'error': err.args[0]}), 409)

        return make_response(jsonify({"message": "Registration Successful"}), 201)
         

# Login user

@app.route('/api/v1/auth/login',  methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        cleaned_data = clean_data(data)
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        # check if the user details exist in the list, otherwise deny access.
        if email == "" or password == "":
            return make_response(jsonify({"message": "Incomplete entry"}), 401)
        user = [user for user in User.users if user.email == email]
        if user:
            if password == user[0].password:
                session['logged_in'] = True
                session['user_id'] = user[0].id
                return make_response(jsonify({"message": "Login Successful"}), 200)


            else:
                return make_response(jsonify({"message": "Wrong Password"}), 409)

        else:
            return make_response(jsonify({"message": "User email is not registered"}), 409)

# reset password
@app.route('/api/v1/auth/reset-password', methods = ['POST'])
def reset_password():
    data = request.get_json()
    cleaned_data = clean_data(data)
    email = cleaned_data.get('email')
    newpassword = cleaned_data.get('newpassword')
       
    user = [user for user in User.users if user.email == email]
    if user:
        try:
            user[0].reset_password(newpassword)
        except AssertionError as err:
            return make_response(jsonify({"error": err.args[0]}), 409)
        return make_response(jsonify({"message": "Reset Successful"}), 201)
    else:
        return make_response(jsonify({"message": "User with that email does not exist"}), 404)

# check  if user is logged in


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return make_response(jsonify({"Unauthorised": "Please login first"}), 401)
    return wrap

# Change password


@app.route('/api/v1/auth/change-password', methods=['POST'])
@is_logged_in
def change_password():
    data = request.get_json()
    cleaned_data = clean_data(data)
    username = cleaned_data.get('username')
    password = cleaned_data.get('password')
    newpassword = cleaned_data.get('newpassword')
    user = [user for user in User.users if user.username == username]
    if user and password != user[0].password:
        return make_response(jsonify({"message": "Enter your Current Password"}), 409)
    elif newpassword == user[0].password:
        return make_response(jsonify({"message": "Use a Different New Password"}), 409)

    else:
        try:
            user[0].reset_password(newpassword)
        except AssertionError as err:
            return make_response(jsonify({"error": err.args[0]}), 409)
    return make_response(jsonify({"message": "Reset Successful"}), 201)

"""USER LOGOUT"""
@app.route('/api/v1/auth/logout', methods=['POST'])
@is_logged_in
def logout():
    session.clear()
    return make_response(jsonify({"message": "Logout Successful"}), 200)

"""CREATE A NEW BUSINESS"""
@app.route('/api/v1/auth/businesses', methods=['POST'])
@is_logged_in
def create_business():
    data = request.get_json()
    cleaned_data = clean_data(data)
    name = cleaned_data.get("name")
    category = cleaned_data.get("category")
    location = cleaned_data.get("location")

    if name is None:
        return make_response(jsonify({"error": "Missing name key"}), 500)

    if category is None:
        return make_response(jsonify({"error": "Missing category key"}), 500)

    if location is None:
        return make_response(jsonify({"error": "Missing location key"}), 500)

    # check if the business details already in the list, otherwise create the object in the list
    available_names = [business.name.lower() for business in Business.businesses]
    user_id = session.get('user_id')
    if name.lower() in available_names:
        return make_response(jsonify({"error": "Business already Exist, use another name"}), 409)

    else:
        try:
            business = Business.register_business(
                name, category, location, user_id)
        except AssertionError as err:
            return jsonify({"error": err.args[0]}), 409
        myresponse = {'name': business.name, 'category': business.category,
                        'location': business.location}
        return make_response(jsonify(myresponse), 201)


"""RETRIEVE ALL BUSINNESSES"""

@app.route('/api/v1/auth/businesses', methods=['GET'])
@is_logged_in
def view_businesses():
    mybusinesses = [{business.id: [business.name, business.category, business.location]
                     for business in Business.businesses}]
    if mybusinesses == [{}]:
        return make_response(jsonify({"businesses": "No Business Entry"}), 404)
    else:
        return make_response(jsonify({"businesses": mybusinesses}), 200)

"""RETRIEVE A PARTICULAR BUSINESS"""

@app.route('/api/v1/auth/businesses/<int:id>/', methods=['GET'])
@is_logged_in
def get_business(id):
    target_business = [business for business in Business.businesses if business.id == id]
    if target_business:
        target_business = target_business[0]
        return make_response(jsonify({"business": {'name': target_business.name,
        'category': target_business.category, 'location': target_business.location}}), 200)
    else:
        return make_response(jsonify({"message": "Business not available", }), 404)

"""UPDATE A BUSINESS"""

@app.route('/api/v1/auth/businesses/<int:id>', methods=['PUT'])
@is_logged_in
def update_business(id):
    data = request.get_json()
    cleaned_data = clean_data(data)

    target_business = [business for business in Business.businesses if business.id == id]
    
    if target_business:
        available_names = [business.name.lower() for business in Business.businesses]

        if data.get("name").lower() in available_names: 
            return make_response(jsonify({"error": "Business already Exist, use another name"}), 409)

        if session.get('user_id') != target_business[0].userid:
            return make_response(jsonify({"message": "You cannot update someones Business", }), 404)
        
        try:
            issuer_id = session.get('user_id')
            target_business[0].update_business(cleaned_data, issuer_id)
        except AssertionError as err:
            return make_response(jsonify({"error": err.args[0]}), 409)
        return make_response(jsonify({"message": "Business Updated" }), 201)
    
    else:
        return make_response(jsonify({"message": "Business not available" }), 404)

"""DELETE A BUSINESS FROM THE SYSTEM"""

@app.route('/api/v1/auth/businesses/<int:id>', methods=['DELETE'])
@is_logged_in
def delete_business(id):
    target_business = [business for business in Business.businesses if business.id == id]
    

    if target_business:
        if session.get('user_id') != target_business[0].userid:
            return make_response(jsonify({"message": "You cannot delete someones Business" }), 409)
        target_business = target_business[0]
        Business.businesses.remove(target_business)
        return make_response(jsonify({"message": "Business deleted", }), 200)
    else:
        return make_response(jsonify({"message": "There is no Business with that ID" }), 404)

"""ADD REVIEWS TO A BUSINESS"""

@app.route('/api/v1/auth/<int:businessid>/reviews', methods=['POST'])
@is_logged_in
def reviews(businessid):
    data = request.get_json()
    description = data.get("description")
    password = data.get('password')
    if description is None:
        return make_response(jsonify({"error": "Check your entry"}), 409)
    if type(description) != str:
        return make_response(jsonify({"error": "Review cannot be an integer"}), 409)

    if description.strip() == "":
        return make_response(jsonify({"error": "Empty review not allowed"}), 409)

    if len(description) < 2:
        return make_response(jsonify({"error": "Review too short"}), 409)

    mybusiness = [
        business for business in Business.businesses if business.id == businessid]
    if mybusiness:
        business_review = Review(description, businessid)
        business_reviews.append(business_review)
        return make_response(jsonify({"message": "Review added Successfully"}), 201)
    else:
        return make_response(jsonify({"message": "Business with that ID does not exist"}), 404)


"""RETRIEVE ALL REVIEWS THAT BELONGS TO A BUSINESS"""
@app.route('/api/v1/auth/<int:businessid>/reviews', methods=['GET'])
@is_logged_in
def myreviews(businessid):
    target_reviews = [{review.id : [review.businessid, review.description] 
    for review in business_reviews if review.businessid == businessid}]
    
    if target_reviews == [{}]:
        return make_response(jsonify({"message": "No Reviews available for that Business"}), 404)
    else:
        return make_response(jsonify({"Reviews": target_reviews})), 200
