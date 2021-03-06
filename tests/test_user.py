import os
from app import app

import unittest
import tempfile
import json
from flask import jsonify

from app.models.user import User


class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.data = {"username": "john",
                     "email": "email@gmail.com", "password": "&._12345",
                      "newpassword":"&._12345"}
        self.data1 = {"": "james", "email": "something@gmail.com",
                      "password": "&._12345"}
        self.data2 = {"username": "Bill",
                      "email": "bill@gmail.com", "password": "&._12345k"}
        self.data3 = {"username": "",
                      "email": "bills@gmail.com", "password": "&._12345", 
                      "newpassword": "&._1234"}
        self.data4 = {"username": "james", "email": "something",
                      "password": "&._12345"}
        self.data5 = {"username": "john",
                     "email": "myemail@gmail.com",
                      "password": ".",}
        self.data6 = {"email": "email@gmail.com", "password": "&._125"}

        self.data7 = {"email": "", "password": "&._12345"}

        self.data8 = {"username": "john",
                      "email": "uhiuhuyguygy", "password": "&__456789"}

        self.data9 = {"username": "john","email": "email@gmail.com",
                      "password": "&._12345", "newpassword": "123456789"}

        self.data10 = {"email":"email@gmail.com", "password": "123456789"}

        self.data11 = {"username": "john",
                     "email": "email@gmail.com", "password": "_12345",
                      "newpassword": "ijihg45"}
        self.data12 = {"username": 1,"email": "username@gmail.com", "password": "&._12345"}
        self.data13 = {"username": "user","email": 2, "password": "&._12345"}
        self.data14 = {"username": "user","email":"username@gmail.com", "password": 3}
        self.data15 = {"username": "john","email": "email@gmail.com",
                       "newpassword": "123456789"}
        self.data16 = {"username": "john","email": "email@gmail.com",
                      "password": "&._12345", "newpassword": 1}
        self.data17 = {"username": "john","email": "email@gmail.com",
                      "password": "&._12345", "newpassword": "g"}              

        

        # Default user
        self.app.post('/api/v1/auth/register',
                      data=json.dumps(self.data), content_type='application/json')

    def tearDown(self):
        del User.users[:]

    def test_missing_username_key_registration(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data1), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["error"], "Missing key")
        self.assertEqual(response.status_code, 500)

    def test_invalid_username_registration(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data3), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["error"], "Invalid username")
        self.assertEqual(response.status_code, 409)

    def test_invalid_email_registrartion(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data4), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["error"], "Invalid email")
        self.assertEqual(response.status_code, 409)

    def test_no_string_username_registrartion(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data12), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["error"], "Invalid username")
        self.assertEqual(response.status_code, 409)

    def test_no_string_email_registrartion(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data13), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["error"], "Invalid email")
        self.assertEqual(response.status_code, 409)

    def test_non_string_password_registrartion(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data14), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["error"], "Invalid password")
        self.assertEqual(response.status_code, 409)

    def test_invalid_password_registration(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data5), content_type='application/json')
        result = json.loads(response.data.decode())
        print('ggggrgrgrgrg', result)
        self.assertEqual(result["error"], "Invalid password")
        self.assertEqual(response.status_code, 409)

    def test_new_user_registration(self):
        response = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data2), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["message"], "Registration Successful")
        self.assertEqual(response.status_code, 201)

    def test_duplicate_user_registration(self):
        response2 = self.app.post(
            '/api/v1/auth/register', data=json.dumps(self.data), content_type='application/json')
        result2 = json.loads(response2.data.decode())
        self.assertEqual(result2["message"], "Email already registered, singup with a different Email")
        self.assertEqual(response2.status_code, 409)

    def test_user_login(self):
        response = self.app.post(
            '/api/v1/auth/login', data=json.dumps(self.data), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["message"], "Login Successful")
        self.assertEqual(response.status_code, 200)

    def test_wrong_password_login(self):
        response = self.app.post(
            '/api/v1/auth/login', data=json.dumps(self.data6), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["message"], "Wrong Password")
        self.assertEqual(response.status_code, 409)

    def test_empty_login(self):
        response = self.app.post(
            '/api/v1/auth/login', data=json.dumps(self.data7), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertTrue(result["message"], "Incomplete entry")
        self.assertEqual(response.status_code, 401)

    def test_unregistered_user_login(self):
        response = self.app.post(
            '/api/v1/auth/login', data=json.dumps(self.data8), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["message"], "User email is not registered")
        self.assertEqual(response.status_code, 409)

    def test_unlogged_in_users(self):
        response = self.app.post('/api/v1/auth/change-password',
                                 data=json.dumps(self.data5), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["Unauthorised"], "Please login first")
        self.assertEqual(response.status_code, 401)

    def test_change_password(self):
        self.app.post('/api/v1/auth/login', data=json.dumps(self.data),
                      content_type='application/json')
        response1 = self.app.post('/api/v1/auth/change-password',
                                  data=json.dumps(self.data9), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "Reset Successful")
        self.assertEqual(response1.status_code, 201)
        response2 = self.app.post(
            '/api/v1/auth/login', data=json.dumps(self.data10), content_type='application/json')
        result2 = json.loads(response2.data.decode())
        self.assertEqual(result2["message"], "Login Successful")
        self.assertEqual(response2.status_code, 200)

    def change_password_with_wrong_email(self):
        self.app.post('/api/v1/auth/login', data=json.dumps(self.data),
                      content_type='application/json')
        response1 = self.app.post('/api/v1/auth/change-password',
                                  data=json.dumps(self.data3), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "User with that email does not exist")

    def test_change_with_same_password(self):
        self.app.post('/api/v1/auth/login', data=json.dumps(self.data),
                      content_type='application/json')
        response1 = self.app.post('/api/v1/auth/change-password',
                                  data=json.dumps(self.data), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "Use a Different New Password")
        self.assertEqual(response1.status_code, 409)


    def test_empty_current_password(self):
        self.app.post('/api/v1/auth/login', data=json.dumps(self.data),
                      content_type='application/json')
        response1 = self.app.post('/api/v1/auth/change-password',
                                  data=json.dumps(self.data15), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "Enter your Current Password")
        self.assertEqual(response1.status_code, 409)
    
    def test_invalid_password_format(self):
        self.app.post('/api/v1/auth/login', data=json.dumps(self.data),
                      content_type='application/json')
        response1 = self.app.post('/api/v1/auth/reset-password',
                                  data=json.dumps(self.data16), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["error"], "Invalid password")
        self.assertEqual(response1.status_code, 409)

    def test_current_password(self):
        self.app.post('/api/v1/auth/login', data=json.dumps(self.data),
                      content_type='application/json')
        response1 = self.app.post('/api/v1/auth/change-password',
                                  data=json.dumps(self.data11), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "Enter your Current Password")
        self.assertEqual(response1.status_code, 409)

    def test_reset_password(self):
        response1 = self.app.post('/api/v1/auth/reset-password',
                                  data=json.dumps(self.data9), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "Reset Successful")
        self.assertEqual(response1.status_code, 201)
        response2 = self.app.post(
            '/api/v1/auth/login', data=json.dumps(self.data10), content_type='application/json')
        result2 = json.loads(response2.data.decode())
        self.assertEqual(result2["message"], "Login Successful")
        self.assertEqual(response2.status_code, 200)

    def test_reset_unregistered_user(self):
        response1 = self.app.post('/api/v1/auth/reset-password',
                                  data=json.dumps(self.data3), content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "User with that email does not exist")


    def test_reset_invalid_password(self):
        response = self.app.post('/api/v1/auth/reset-password',
                                  data=json.dumps(self.data17), content_type='application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["error"], "Invalid password")
        self.assertEqual(response.status_code, 409)


    def test_logout(self):
        response = self.app.post(
            '/api/v1/auth/login', data=json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response1 = self.app.post(
            '/api/v1/auth/logout', content_type='application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "Logout Successful")
        self.assertEqual(response1.status_code, 200)

    

if __name__ == '__main__':
    unittest.main()
