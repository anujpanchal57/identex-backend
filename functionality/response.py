from json import dumps
from flask import jsonify, make_response

def forbiddenResponse():
    response = {'response': 'Unauthorized Access'}
    return jsonify(response), 403

def tokenExpiredResponse():
    return jsonify({"response": "Session expired. Please login again"}), 403

def incompleteResponse(message):
    response = {'response': 'Incomplete request! Missing param:'+str(message)}
    return jsonify(response), 400

def customResponse(keys_values,status=200):
    return jsonify(keys_values), status

def errorResponse(e,status=400):
    response = {'response': str(e)}
    return jsonify(response), status

def unknownuser():
    return jsonify({"response": "User not present"}), 403

def emailNotFound():
    return jsonify({"response": "We cannot find an account with this email address"}), 400