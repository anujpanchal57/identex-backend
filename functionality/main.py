import hashlib
import os
import random
import sys
import time
import traceback
from pprint import pprint

from flask import Flask, request, jsonify
from flask_cors import CORS
import platform
import jwt


app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])

sys.path.append(app_name)

app = Flask(__name__)
CORS(app)

# test
from functionality import DictionaryOps, GenericOps, response
from models.GenericEmails import Generics
from functionality.Logger import Logger
from validations import Validate
from exceptions import exceptions
from functools import wraps
from utility import DBConnectivity, conf, Implementations
from database.BuyerOps import Buyer
from database.BuyerUserOps import BUser
from database.SupplierOps import Supplier
from database.SupplierUserOps import SUser
from database.BuyerTeamOps import BuyerTeam
from database.AuthorizationOps import Authorization

# Validates access token for buyer
def validate_buyer_access_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        try:
            token = request.headers.get('X-HTTP-ACCESS-TOKEN')
            data = DictionaryOps.set_primary_key(request.json, 'email')
            buser = BUser(data['_id'])
            if not buser.is_buser(data['_id']):
                return response.unknownuser()
            auth = buser.decode_auth_toke(token.split(":")[0])
            if isinstance(auth, dict):
                if auth['user'] == data['_id']:
                    return f(*args, **kwargs)
                return response.forbiddenResponse()
            # write logout logic for the buser
            if Authorization(token).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="expired"):
                return response.tokenExpiredResponse()
        except TypeError as e:
            return response.incompleteResponse(str(e))
        except Exception as e:
            return response.errorResponse(e)
    return wrapped

# Validates access token for supplier
def validate_supplier_access_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        try:
            token = request.headers.get('X-HTTP-ACCESS-TOKEN')
            data = DictionaryOps.set_primary_key(request.json, 'email')
            suser = SUser(data['_id'])
            if not suser.is_suser(data['_id']):
                return response.unknownuser()
            auth = suser.decode_auth_toke(token)
            if isinstance(auth, dict):
                if auth['user'] == data['_id']:
                    return f(*args, **kwargs)
                return response.forbiddenResponse()
            # write logout logic for the buser
            if Authorization(token).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="expired"):
                return response.tokenExpiredResponse()
        except TypeError as e:
            return response.incompleteResponse(str(e))
        except Exception as e:
            return response.errorResponse(e)
    return wrapped

# POST request for buyer signup authentication
@app.route("/buyer/signup", methods=["POST"])
def buyer_signup_auth():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        existing_domain = False
        domain_name = data['_id'].split('@')[1]
        is_buser = BUser.is_buser(data['_id'])
        if not is_buser:
            if domain_name not in Generics().mail_providers:
                existing_domain = BUser.is_buser_domain_registered(data['_id'])

                if not existing_domain:
                    buyer_id = Buyer().add_buyer(company_name=data['company_name'], domain_name=domain_name)
                    BUser().add_buser(email=data['_id'], name=data['name'], buyer_id=buyer_id, mobile_no=data['mobile_no'], password=data['password'], role="admin")
                    BuyerTeam().create_team(team_name=Implementations.default_bteam_name, buyer_id=buyer_id, members=[data['_id']])
                    # Send verification email
                    return response.customResponse({"response": "Thank you for signing up with Identex. Please enter the OTP sent to you on your email address"})
                else:
                    buyer_id = existing_domain['buyer_id']
                    buyer = Buyer(buyer_id)
                    BUser().add_buser(email=data['_id'], name=data['name'], buyer_id=buyer_id, mobile_no=data['mobile_no'], password=data['password'], role="employee")
                    first_team_id = BuyerTeam.generate_team_id(buyer_id, Implementations.default_bteam_name)
                    BuyerTeam(first_team_id).add_member(data['_id'])
                    # Send verification email
                    return response.customResponse({"response": "Thank you for signing up with Identex. Please enter the OTP sent to your email address"})
            else:
                buyer_id = Buyer().add_buyer(company_name=data['company_name'], domain_name=domain_name)
                BUser().add_buser(email=data['_id'], name=data['name'], buyer_id=buyer_id, mobile_no=data['mobile_no'], password=data['password'], role="admin")
                BuyerTeam().create_team(team_name=Implementations.default_bteam_name, buyer_id=buyer_id, members=[data['_id']])
                # Send verification email
                return response.customResponse({"response": "Thank you for signing up with Identex. Please enter the OTP sent to your email address"})
        return response.errorResponse("User already exists. Try logging in instead")

    except Exception as e:
        log = Logger(module_name='/buyer/signup', function_name='buyer_signup_auth()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for login verification of buyer
@app.route("/buyer/login", methods=["POST"])
def buyer_login_verify():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not BUser.is_buser(data['_id']):
            return response.errorResponse("We cannot find an account with this email address")
        buser = BUser(data['_id'])
        buyer = Buyer(buser.get_buyer_id())
        if buser.get_password() != data['password']:
            return response.errorResponse("You have entered incorrect password")
        if not buyer.get_activation_status():
            return response.errorResponse("Your company account has not been activated. Please contact identex team for activation")
        if not buser.get_status():
            return response.errorResponse("Please verify your email and then try logging in")
        auth_id = buser.encode_auth_token() + ":" + GenericOps.generate_token_for_login()
        auth = Authorization().login_user(auth_id=auth_id, buyer_id=buser.get_buyer_id(), logged_in=GenericOps.get_current_timestamp(), email=data['_id'], device_name=request.headers.get('device-name'))
        if auth:
            return response.customResponse({"response": "Logged in successfully",
                                            "details": {
                                                "_id": data['_id'],
                                                "name": buser.get_name(),
                                                "mobile_no": buser.get_mobile_no(),
                                                "buyer_id": buser.get_buyer_id(),
                                                "access_token": auth_id,
                                                "is_admin": buser.is_admin(),
                                                "activation_status": buyer.get_activation_status(),
                                                "subscription_plan": buyer.get_subscription_plan(),
                                                "auto_join": buyer.get_auto_join(),
                                                "company_logo": buyer.get_company_logo(),
                                                "default_currency": buyer.get_default_currency(),
                                                "created_at": buser.get_created_at(),
                                                "updated_at": buser.get_updated_at()
                                            }})
        return response.errorResponse("Invalid credentials")

    except Exception as e:
        log = Logger(module_name='/buyer/login', function_name='buyer_login_verify()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for login verification of buyer
@app.route("/supplier/login", methods=["POST"])
def supplier_login_verify():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not SUser.is_suser(data['_id']):
            return response.errorResponse("We cannot find an account with this email address")
        suser = SUser(data['_id'])
        supplier = Supplier(suser.get_buyer_id())
        if suser.get_password() != data['password']:
            return response.errorResponse("You have entered incorrect password")
        if not suser.get_status():
            return response.errorResponse("Please verify your email and then try logging in")
        auth_id = suser.encode_auth_token() + ":" + GenericOps.generate_token_for_login()
        auth = Authorization().login_user(auth_id=auth_id, buyer_id=suser.get_buyer_id(),
                                          logged_in=GenericOps.get_current_timestamp(), email=data['_id'],
                                          device_name=request.headers.get('device-name'))
        if auth:
            return response.customResponse({"response": "Logged in successfully",
                                            "details": {
                                                "_id": data['_id'],
                                                "name": suser.get_name(),
                                                "mobile_no": suser.get_mobile_no(),
                                                "access_token": auth_id,
                                                "company_logo": supplier.get_company_logo(),
                                                "status": suser.get_status(),
                                                "role": suser.get_role(),
                                                "activation_status": supplier.get_activation_status(),
                                                ""
                                                "created_at": suser.get_created_at(),
                                                "updated_at": suser.get_updated_at()
                                            }})
        return response.errorResponse("Invalid credentials")

    except Exception as e:
        log = Logger(module_name='/supplier/login', function_name='supplier_login_verify()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for buyer logout
@app.route("/buyer/logout", methods=['POST'])
@validate_buyer_access_token
def buyer_logout():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if Authorization(request.headers.get('X-HTTP-ACCESS-TOKEN')).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="logout"):
            return response.customResponse({"response": "Logged out successfully"})

    except Exception as e:
        log = Logger(module_name='/buyer/logout', function_name='buyer_logout()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for buyer logout
@app.route("/supplier/logout", methods=['POST'])
@validate_supplier_access_token
def supplier_logout():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if Authorization(request.headers.get('X-HTTP-ACCESS-TOKEN')).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="logout"):
            return response.customResponse({"response": "Logged out successfully"})

    except Exception as e:
        log = Logger(module_name='/supplier/logout', function_name='supplier_logout()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, threaded=True)
