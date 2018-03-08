# import os
import app
import unittest
import tempfile
import json
from flask import jsonify

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
        self.data = {'Id':"1", "name":"easyE", "cartegory":"hardware", "location":"Mombasa", "Review":"Selling hardware products" }
        self.data2 = {'Id':"2", "name":"Dlinks", "cartegory":"software", "location":"Nairobi", "Review":"Selling software products" }
        

    def test_create_business(self):
        response = self.app.post('/api/v1/auth/create_business', data = json.dumps(self.data), content_type = 'application/json')
        result = json.loads(response.data.decode())
        self.assertEqual(result["message"], "Created Successful")
        self.assertEqual(response.status_code, 201)

    def test_duplicate_business(self):
        response1 = self.app.post('/api/v1/auth/create_business', data = json.dumps(self.data2) , content_type = 'application/json')
        result1 = json.loads(response1.data.decode())
        self.assertEqual(result1["message"], "Created Successful")
        self.assertEqual(response1.status_code, 201)
        response2 = self.app.post('/api/v1/auth/create_business', data = json.dumps(self.data2) , content_type = 'application/json')
        result2 = json.loads(response2.data.decode())
        self.assertEqual(result2["message"], "Business Exist")
        self.assertEqual(response2.status_code, 409)
    


if __name__ == '__main__':
    unittest.main()