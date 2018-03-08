from flask import Flask, request, jsonify, make_response
import json 
from models.user import User
from models.business import Business


app = Flask(__name__)

users = []
businesses = []

#Register user and ssaving the details in a list called users
@app.route('/v1/register_user',  methods = ['POST'])
def register_user():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    #check if the user details already in the list, otherwise add the details in the list
    available_emails = [x.email for x in users]
    if email in available_emails:
        return make_response(jsonify({"status": "NOT_ACCEPTABLE", "message": "User Details Exist"}), 406)
    else:
        user = User(username, email, password)
        users.append(user)
    return make_response(jsonify({"status": "ok", "message": "Registered Successful"}), 201)

#Login user
@app.route('/v1/user_login',  methods = ['POST'])
def user_login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    #check if the user details exist in the list, otherwise deny access.
    user = [x for x in users if x.username == username]
    if user:
        if password == user[0].password:
            return make_response(jsonify({"status": "ok", "message": "Login Successful"}), 200)

        else:
            return make_response(jsonify({"status": "Forbidden", "message": "Wrong Password"}), 406)

    else:
        return make_response(jsonify({"status": "Forbidden", "message": "Wrong Login Details"}), 406)
   
#Reset password
@app.route('/v1/reset_password', methods = ['POST'])
def reset_password():
    data = request.get_json()
    password = data['password']
    user = [x for x in users if x.password == password]
    if user and password == user[0].password:
        return make_response(jsonify({"status": "Forbidden", "message": "Type Different Password"}), 406)
    else:
        User.password = password
        return make_response(jsonify({"status": "ok", "message": "Reset Successful"}), 201)

#Create user
@app.route('/v1/create_business', methods = ['POST'])
def create_business():
    data = request.get_json()
    Id = data['Id']
    name = data["name"]
    cartegory = data["cartegory"]
    location = data["location"]
    description = data["Description"]
     #check if the business details already in the list, otherwise create the object in the list
    available_Ids = [x.Id for x in businesses]
    if Id in available_Ids:
        return make_response(jsonify({"status": "NOT_ACCEPTABLE", "message": "Business Exist"}), 406)
    else:
        business = Business(Id, name, cartegory, location, description)
        businesses.append(business)
    return make_response(jsonify({"status": "ok", "message": "Created Successful"}), 201)





if __name__ == '__main__':

    app.run(debug=True)