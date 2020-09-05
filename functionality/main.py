import hashlib
import os
import random
import sys
import time
import traceback
from pprint import pprint

from flask import Flask, request
from flask_cors import CORS
import platform
import jwt
import flask


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
from database.AuthorizationOps import Authorization
from multiprocessing import Process
from database.VerificationOps import Verification
from database.SupplierRelationshipOps import SupplierRelationship
from Integrations.AWSOps import AWS
from database.InvitedSupplierOps import InviteSupplier
from database.LotOps import Lot
from database.ProductOps import Product
from database.RequisitionOps import Requisition
from database.DocumentOps import Document
from database.ActivityLogsOps import ActivityLogs
from database.QuotationOps import Quotation
from database.QuoteOps import Quote
from functionality import EmailNotifications
from database.JoinOps import Join
from database.MessageOps import Message
from database.MessageDocumentOps import MessageDocument
from database.ProductMasterOps import ProductMaster
from database.OrderOps import Order
from database.Reports import Reports

##################################### ACCESS TOKEN VALIDATORS (DECORATORS) ############################################

# Validates access token for buyer
def validate_buyer_access_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        try:
            token = request.headers.get('X-HTTP-ACCESS-TOKEN')
            data = DictionaryOps.set_primary_key(request.json, 'email')
            data['_id'] = data['_id'].lower()
            buser = BUser(data['_id'])
            if not buser.is_buser(data['_id']):
                return response.unknownuser()
            auth = buser.decode_auth_token(token.split(":")[0])
            # Check if the token has expired or not
            if isinstance(auth, dict):
                # check whether the email ID is same
                if auth['user'] == data['_id']:
                    # Check in redis for the token
                    if DBConnectivity.get_redis_key(token) is not None:
                        return f(*args, **kwargs)
                    else:
                        Authorization(token).logout_user(logged_out=GenericOps.get_current_timestamp(),
                                                         action_type="expired")
                        return response.tokenExpiredResponse()
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
            data['_id'] = data['_id'].lower()
            suser = SUser(data['_id'])
            if not suser.is_suser(data['_id']):
                return response.unknownuser()
            auth = suser.decode_auth_token(token.split(":")[0])
            # Check if the token has expired or not
            if isinstance(auth, dict):
                # check whether the email ID is same
                if auth['user'] == data['_id']:
                    # Check for the token in redis
                    if DBConnectivity.get_redis_key(token) is not None:
                        return f(*args, **kwargs)
                    else:
                        Authorization(token).logout_user(logged_out=GenericOps.get_current_timestamp(),
                                                         action_type="expired")
                        return response.tokenExpiredResponse()
                return response.forbiddenResponse()
            # write logout logic for the buser
            if Authorization(token).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="expired"):
                return response.tokenExpiredResponse()
        except TypeError as e:
            return response.incompleteResponse(str(e))
        except Exception as e:
            return response.errorResponse(e)
    return wrapped

# Validates access token for supplier/buyer
def validate_access_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        try:
            token = request.headers.get('X-HTTP-ACCESS-TOKEN')
            client_type = request.json['client_type']
            data = DictionaryOps.set_primary_key(request.json, 'email')
            data['_id'] = data['_id'].lower()
            if client_type.lower() == "supplier":
                if not SUser.is_suser(data['_id']):
                    return response.unknownuser()
                else:
                    suser = SUser(data['_id'])
                    auth = suser.decode_auth_token(token.split(":")[0])
            else:
                if not BUser.is_buser(data['_id']):
                    return response.unknownuser()
                else:
                    buser = BUser(data['_id'])
                    auth = buser.decode_auth_token(token.split(":")[0])
            # Check if the token has expired or not
            if isinstance(auth, dict):
                # check whether the email ID is same
                if auth['user'] == data['_id']:
                    # Check for the token in redis
                    if DBConnectivity.get_redis_key(token) is not None:
                        return f(*args, **kwargs)
                    else:
                        Authorization(token).logout_user(logged_out=GenericOps.get_current_timestamp(),
                                                         action_type="expired")
                        return response.tokenExpiredResponse()
                return response.forbiddenResponse()
            # write logout logic for the buser
            if Authorization(token).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="expired"):
                return response.tokenExpiredResponse()
        except TypeError as e:
            return response.incompleteResponse(str(e))
        except Exception as e:
            return response.errorResponse(e)
    return wrapped

################################### AUTHENTICATION SECTION ############################################################

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
                existing_domain = Buyer.is_buyer_domain_registered(data['_id'])
                if existing_domain:
                    auto_join = existing_domain['auto_join']
                if not existing_domain:
                    buyer_id = Buyer().add_buyer(company_name=data['company_name'], domain_name=domain_name)
                    BUser().add_buser(email=data['_id'], name=data['name'], buyer_id=buyer_id, mobile_no=data['mobile_no'], password=data['password'], role="admin")
                    # Send verification email
                    token = GenericOps.generate_email_verification_token()
                    if Verification(name="verify_email").add_auth_token(token_id=token, user_id=data['_id'], user_type="buyer"):
                        link = conf.ENV_ENDPOINT + conf.email_endpoints['buyer']['email_verification']['page_url'] + "?id=" + data['_id'] + "&token=" + token
                        p = Process(target=EmailNotifications.send_template_mail, kwargs={"template": conf.email_endpoints['buyer']['email_verification']['template_id'],
                                                                                          "subject": conf.email_endpoints['buyer']['email_verification']['subject'],
                                                                                          "verification_link": link,
                                                                                          "recipients": [data['_id']]})
                        p.start()
                        return response.customResponse({"response": "Thank you for signing up with Identex. We have sent you a verification link on your email"})
                else:
                    if auto_join:
                        buyer_id = existing_domain['buyer_id']
                    else:
                        buyer_id = Buyer().add_buyer(company_name=data['company_name'], domain_name=domain_name)
                    BUser().add_buser(email=data['_id'], name=data['name'], buyer_id=buyer_id, mobile_no=data['mobile_no'], password=data['password'], role="employee")
                    # Send verification email
                    token = GenericOps.generate_email_verification_token()
                    if Verification(name="verify_email").add_auth_token(token_id=token, user_id=data['_id'], user_type="buyer"):
                        link = conf.ENV_ENDPOINT + conf.email_endpoints['buyer']['email_verification']['page_url'] + "?id=" + data['_id'] + "&token=" + token
                        p = Process(target=EmailNotifications.send_template_mail, kwargs={
                            "template": conf.email_endpoints['buyer']['email_verification']['template_id'],
                            "subject": conf.email_endpoints['buyer']['email_verification']['subject'],
                            "verification_link": link,
                            "recipients": [data['_id']]})
                        p.start()
                        return response.customResponse({"response": "Thank you for signing up with Identex. We have sent you a verification link on your email"})
            else:
                return response.errorResponse("Please enter your business email")
        return response.errorResponse("User already exists. Try logging in instead")

    except Exception as e:
        log = Logger(module_name='/buyer/signup', function_name='buyer_signup_auth()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for verifying buyer business email
@app.route("/buyer/is-business-email", methods=["POST"])
def is_business_email_buyer():
    try:
        data = request.json
        if data['email'].split("@")[1] not in Generics().mail_providers:
            return response.customResponse({"is_business_email": True})
        return response.customResponse({"is_business_email": False})

    except Exception as e:
        log = Logger(module_name='/buyer/is-business-email', function_name='is_business_email_buyer()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for login verification of buyer
@app.route("/buyer/login", methods=["POST"])
def buyer_login_verify():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not BUser.is_buser(data['_id']):
            return response.emailNotFound()
        buser = BUser(data['_id'])
        buyer = Buyer(buser.get_buyer_id())
        if buser.get_password() != data['password']:
            return response.errorResponse("You have entered incorrect password")
        if not buyer.get_activation_status():
            return response.errorResponse("Your company account has not been activated. Please contact identex team for activation")
        if not buser.get_status():
            return response.errorResponse("Please verify your email and then try logging in")
        auth_id = buser.encode_auth_token() + ":" + GenericOps.generate_token_for_login()
        auth = Authorization().login_user(auth_id=auth_id, entity_id=buser.get_buyer_id(), logged_in=GenericOps.get_current_timestamp(),
                                          email=data['_id'], device_name=request.headers.get('device-name'), type="buyer")
        if auth:
            # Set the access token in redis
            DBConnectivity.set_redis_key(auth_id, str(True), conf.jwt_expiration)
            return response.customResponse({"response": "Logged in successfully",
                                            "details": {
                                                "_id": data['_id'],
                                                "name": buser.get_name(),
                                                "mobile_no": buser.get_mobile_no(),
                                                "buyer_id": buser.get_buyer_id(),
                                                "access_token": auth_id,
                                                "is_admin": buser.is_admin(),
                                                "company_name": buyer.get_company_name(),
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

# POST request for email verification of buyer
@app.route("/buyer/verify-email", methods=["POST"])
def buyer_verify_email():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        is_buser = BUser.is_buser(data['_id'])
        buyer_id = BUser(data['_id']).get_buyer_id()
        if is_buser:
            if Verification(_id=data['token'], name="verify_email").verify_auth_token(user_type="buyer"):
                BUser(data['_id']).set_status(status=True)
                activation_status = Buyer(buyer_id).get_activation_status()
                if activation_status:
                    return response.customResponse({"response": "Your email has been verified successfully", "activation_status": activation_status})
                return response.customResponse({"response": "Your company account has not been activated", "activation_status": activation_status})
            return response.errorResponse("Link seems to be broken")
        return response.emailNotFound()

    except Exception as e:
        log = Logger(module_name='/buyer/verify-email', function_name='buyer_verify_email()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for authentication of forgot password for buyer
@app.route("/buyer/forgot-password/auth", methods=["POST"])
def buyer_forgot_password_auth():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not BUser.is_buser(data['_id']):
            return response.emailNotFound()
        token = GenericOps.generate_forgot_password_token()
        if Verification(_id="", name="forgot_password").add_auth_token(token_id=token, user_id=data['_id'], user_type="buyer"):
            DBConnectivity.set_redis_key(data['_id'] + "forgot_password", token, timeout=86400)
            link = conf.ENV_ENDPOINT + conf.email_endpoints['buyer']['forgot_password']['page_url'] + "?id=" + data['_id'] + "&token=" + token
            # send an email
            p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [data['_id']],
                                                                              "subject": conf.email_endpoints['buyer']['forgot_password']['subject'],
                                                                              "template": conf.email_endpoints['buyer']['forgot_password']['template_id'],
                                                                              "forgot_password_link": link,
                                                                              "user": BUser(data['_id']).get_first_name()})
            p.start()
            return response.customResponse({"response": "We have sent a link on your registered email. You can click on the link to reset password"})
        return response.emailNotFound()

    except Exception as e:
        log = Logger(module_name='/buyer/forgot-password/auth', function_name='buyer_forgot_password_auth()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for authentication of forgot password for buyer
@app.route("/buyer/forgot-password/token/verify", methods=["POST"])
def buyer_forgot_password_verify_token():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not BUser.is_buser(data['_id']):
            return response.emailNotFound()
        token = Verification(data['token'], "forgot_password")
        if token.is_valid_token():
            if DBConnectivity.get_redis_key(data['_id'] + "forgot_password"):
                return response.customResponse({"is_valid": True, "response": "Token verified successfully"})
            token.delete_verification_token()
            return response.customResponse({"is_valid": False, "response": "Link seems to be broken"})
        return response.customResponse({"is_valid": False, "response": "Link seems to be broken"})

    except Exception as e:
        log = Logger(module_name='/buyer/forgot-password/token/verify', function_name='buyer_forgot_password_verify_token()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for verifying the buyer's forgot password request
@app.route("/buyer/forgot-password/verify", methods=["POST"])
def buyer_forgot_password_verify():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not BUser.is_buser(data['_id']):
            return response.emailNotFound()
        if 'password' not in data:
            return response.errorResponse("Bad request")
        if len(data['password']) == 0:
            return response.errorResponse("Password cannot be left as blank")
        buser = BUser(data['_id'])
        if Verification(_id=data['token'], name="forgot_password").verify_auth_token(user_type="buyer"):
            buser.set_password(data['password'])
            DBConnectivity.delete_redis_key(data['_id'] + "forgot_password")
            # Delete all the active login sessions from redis
            active_tokens = Authorization.get_active_tokens(email=data['_id'], type="buyer")
            if len(active_tokens) > 0:
                for token in active_tokens:
                    Authorization(token['auth_id']).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="password_reset")
                    DBConnectivity.delete_redis_key(token['auth_id'])
            return response.customResponse({"response": "Your password has been updated. You have been logged out of the other devices"})
        return response.errorResponse("Link seems to be broken")

    except Exception as e:
        log = Logger(module_name='/buyer/forgot-password/verify', function_name='buyer_forgot_password_verify()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for authentication of forgot password for supplier
@app.route("/supplier/forgot-password/auth", methods=["POST"])
def supplier_forgot_password_auth():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not SUser.is_suser(data['_id']):
            return response.emailNotFound()
        token = GenericOps.generate_forgot_password_token()
        if Verification(name="forgot_password").add_auth_token(token_id=token, user_id=data['_id'], user_type="supplier"):
            DBConnectivity.set_redis_key(data['_id'] + "forgot_password", token, timeout=86400)
            link = conf.SUPPLIERS_ENDPOINT + conf.email_endpoints['supplier']['forgot_password']['page_url'] + "?id=" + data['_id'] + "&token=" + token
            # send an email
            p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [data['_id']],
                                                                              "subject": conf.email_endpoints['supplier']['forgot_password']['subject'],
                                                                              "template": conf.email_endpoints['supplier']['forgot_password']['template_id'],
                                                                              "forgot_password_link": link,
                                                                              "user": SUser(data['_id']).get_first_name()})
            p.start()
            return response.customResponse({"response": "We have sent a link on your registered email. You can click on the link to reset password"})
        return response.emailNotFound()

    except Exception as e:
        log = Logger(module_name='/supplier/forgot-password/auth', function_name='supplier_forgot_password_auth()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for authentication of forgot password for supplier
@app.route("/supplier/forgot-password/token/verify", methods=["POST"])
def supplier_forgot_password_verify_token():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not SUser.is_suser(data['_id']):
            return response.emailNotFound()
        token = Verification(data['token'], "forgot_password")
        if token.is_valid_token():
            if DBConnectivity.get_redis_key(data['_id'] + "forgot_password"):
                return response.customResponse({"is_valid": True, "response": "Token verified successfully"})
            token.delete_verification_token()
            return response.customResponse({"is_valid": False, "response": "Link seems to be broken"})
        return response.customResponse({"is_valid": False, "response": "Link seems to be broken"})

    except Exception as e:
        log = Logger(module_name='/supplier/forgot-password/token/verify', function_name='supplier_forgot_password_verify_token()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for verifying the supplier's forgot password request
@app.route("/supplier/forgot-password/verify", methods=["POST"])
def supplier_forgot_password_verify():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not SUser.is_suser(data['_id']):
            return response.emailNotFound()
        if 'password' not in data:
            return response.errorResponse("Bad request")
        if len(data['password']) == 0:
            return response.errorResponse("Password cannot be left as blank")
        suser = SUser(data['_id'])
        if Verification(_id=data['token'], name="forgot_password").verify_auth_token(user_type="supplier"):
            suser.set_password(data['password'])
            DBConnectivity.delete_redis_key(data['_id'] + "forgot_password")
            # Delete all the active login sessions from redis
            active_tokens = Authorization.get_active_tokens(email=data['_id'], type="supplier")
            if len(active_tokens) > 0:
                for token in active_tokens:
                    Authorization(token['auth_id']).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="password_reset")
                    DBConnectivity.delete_redis_key(token['auth_id'])
            return response.customResponse({"response": "Your password has been updated. You have been logged out of the other devices"})
        return response.errorResponse("Link seems to be broken")

    except Exception as e:
        log = Logger(module_name='/supplier/forgot-password/verify', function_name='supplier_forgot_password_verify()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for login verification of buyer
@app.route("/supplier/login", methods=["POST"])
def supplier_login_verify():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if not SUser.is_suser(data['_id']):
            return response.emailNotFound()
        suser = SUser(data['_id'])
        supplier = Supplier(suser.get_supplier_id())
        if suser.get_password() != data['password']:
            return response.errorResponse("You have entered incorrect password")
        if not suser.get_status():
            return response.errorResponse("Please verify your email and then try logging in")
        auth_id = suser.encode_auth_token() + ":" + GenericOps.generate_token_for_login()
        auth = Authorization().login_user(auth_id=auth_id, entity_id=suser.get_supplier_id(),
                                          logged_in=GenericOps.get_current_timestamp(), email=data['_id'],
                                          device_name=request.headers.get('device-name'), type="supplier")
        if auth:
            # Set the access token in redis
            DBConnectivity.set_redis_key(auth_id, str(True), conf.jwt_expiration)
            return response.customResponse({"response": "Logged in successfully",
                                            "details": {
                                                "supplier_id": suser.get_supplier_id(),
                                                "email": data['_id'],
                                                "name": suser.get_name(),
                                                "mobile_no": suser.get_mobile_no(),
                                                "access_token": auth_id,
                                                "company_name": supplier.get_company_name(),
                                                "company_logo": supplier.get_company_logo(),
                                                "status": suser.get_status(),
                                                "role": suser.get_role(),
                                                "activation_status": supplier.get_activation_status(),
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
            # Delete the access token in redis
            DBConnectivity.delete_redis_key(request.headers.get('X-HTTP-ACCESS-TOKEN'))
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
            # Delete the access token in redis
            DBConnectivity.delete_redis_key(request.headers.get('X-HTTP-ACCESS-TOKEN'))
            return response.customResponse({"response": "Logged out successfully"})

    except Exception as e:
        log = Logger(module_name='/supplier/logout', function_name='supplier_logout()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for changing the password of buyer and supplier
@app.route("/password/update", methods=['POST'])
@validate_access_token
def update_password():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        user = BUser(data['_id']) if data['client_type'].lower() == "buyer" else SUser(data['_id'])
        current_password = user.get_password()
        if current_password != data['current_password']:
            return response.errorResponse("Please ensure that you have entered your current password correctly")
        if current_password == data['new_password']:
            return response.errorResponse("Please ensure that your current password and new password are not the same")
        # Changing the password
        if user.set_password(data['new_password']):
            return response.customResponse({"response": "Password changed successfully"})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name='/password/update', function_name='update_password()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request uploading documents
@app.route('/documents/upload', methods=['POST'])
@validate_access_token
def upload_documents():
    try:
        data = DictionaryOps.set_primary_key(request.json, 'email')
        cloud = AWS('s3')
        result = []
        for document in data['documents']:
            upload_file_name = GenericOps.generate_aws_file_path(client_type=data['client_type'], client_id=data['uploaded_by'],
                                                                 document_type=document['document_name'].split(".")[1])
            uploaded = cloud.upload_file_from_base64(base64_string=document['base64'], path=upload_file_name)
            document['document_url'] = uploaded
            document['uploaded_on'] = GenericOps.get_current_timestamp()
            del document['base64']
            result.append(document)
        return response.customResponse({"documents": result, "message": "Document(s) uploaded successfully!"})

    except Exception as e:
        log = Logger(module_name="/documents/upload", function_name="upload_documents()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request uploading documents
@app.route('/buyer/activation-status/update', methods=['POST'])
def buyer_activation_status_update():
    try:
        data = request.json
        data['email'] = data['email'].lower()
        key = request.headers.get('IDNTX-SECRET-KEY')
        if key == conf.BUYER_ACTIVATION_SECRET_KEY:
            buser = BUser(data['email'])
            buyer_id = buser.get_buyer_id()
            if Buyer(buyer_id).update_activation_status(data['activation_status']):
                p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [data['email']],
                                                                                  "subject": conf.email_endpoints['buyer']['welcome_mail']['subject'],
                                                                                  "template": conf.email_endpoints['buyer']['welcome_mail']['template_id'],
                                                                                  "USER": buser.get_first_name()})
                p.start()
                return response.customResponse({"response": "Account activated successfully"})
            return response.errorResponse("Oops, some error occured")
        return response.errorResponse("Please recheck and send the correct secret key")

    except Exception as e:
        log = Logger(module_name="/buyer/activation-status/update", function_name="buyer_activation_status_update()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### BUYER RFQ SECTION #########################################################

# POST request for buyer creating a new RFQ
@app.route("/buyer/rfq/create", methods=["POST"])
@validate_buyer_access_token
def buyer_create_rfq():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buser = BUser(data['_id'])
        buyer_id = data['buyer_id']
        buyer = Buyer(buyer_id)
        if len(data['invited_suppliers']) == 0:
            return response.errorResponse("Please invite atleast one supplier in order to create RFQ")

        if len(data['products']) == 0:
            return response.errorResponse("Please add atleast one product in order to create RFQ")

        document_ids, invited_suppliers_ids = [], []
        # Create the requisition
        deadline = GenericOps.get_calculated_timestamp(date_time=data['deadline'], op_tz=data['timezone'])
        # Deadline validation
        if GenericOps.get_current_timestamp_of_timezone(data['timezone']) + Implementations.deadline_change_time_factor > deadline:
            return response.errorResponse("Please set a deadline of more than 30 mins from the current time")
        utc_deadline = GenericOps.convert_datetime_to_utc_datetimestring(data['deadline'], op_tz=data['timezone'])
        data['submission_limit'] = data['submission_limit'] if 'submission_limit' in data else conf.default_submission_limit
        requisition_id = Requisition("").add_requisition(requisition_name=data['lot']['lot_name'], timezone=data['timezone'],
                                                         currency=data['currency'], buyer_id=buyer_id, deadline=deadline,
                                                         utc_deadline=utc_deadline, submission_limit=data['submission_limit'])
        # Add the invited suppliers
        suppliers = []
        for supplier in data['invited_suppliers']:
            supp = [requisition_id, "rfq", supplier, GenericOps.get_current_timestamp(), True]
            supp = tuple(supp)
            suppliers.append(supp)
        invited_suppliers_ids = InviteSupplier("").insert_many(suppliers)

        # Create the lot
        lot_id = Lot("").add_lot(requisition_id=requisition_id, lot_name=data['lot']['lot_name'], lot_description=data['lot']['lot_description'])

        # Insert the products
        for product in data['products']:
            product_id = Product("").add_product(lot_id=lot_id, buyer_id=buyer_id, product_id=product['product_id'],
                                                 product_description=product['product_description'], unit=product['unit'],
                                                 quantity=product['quantity'])
            if len(product['documents']) > 0:
                documents = []
                for document in product['documents']:
                    doc = [product_id, "product", document['document_url'], document['document_type'], document['document_name'],
                           document['uploaded_on'], data['_id'], "buyer"]
                    doc = tuple(doc)
                    documents.append(doc)
                document_ids += Document("").insert_many(documents)

        # Insert the documents
        documents = []
        if len(data['specification_documents']) > 0:
            for document in data['specification_documents']:
                doc = [requisition_id, "rfq", document['document_url'], document['document_type'], document['document_name'],
                       document['uploaded_on'], data['_id'], "buyer"]
                doc = tuple(doc)
                documents.append(doc)
            document_ids += Document("").insert_many(documents)

        # Adding activity performed to the log
        ActivityLogs("").add_activity(activity="Create RFQ", done_by=data['_id'], operation_id=requisition_id, operation_type="rfq",
                                      type_of_user="buyer", user_id=data['buyer_id'], ip_address=flask.request.remote_addr,
                                      name=buser.get_name(), company_name=buyer.get_company_name())

        # Trigger the email alert to invited suppliers
        invited_suppliers = Join().get_invited_suppliers(operation_id=requisition_id, operation_type="rfq")
        buyer_company_name = buyer.get_company_name()
        rfq_link = conf.SUPPLIERS_ENDPOINT + conf.email_endpoints['supplier']['rfq_created']['page_url']
        subject = conf.email_endpoints['supplier']['rfq_created']['subject'].replace("{{buyer_company}}", buyer_company_name).replace("{{lot_name}}", data['lot']['lot_name'])
        for supplier in invited_suppliers:
            p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [supplier['email']],
                                                                              "template": conf.email_endpoints['supplier']['rfq_created']['template_id'],
                                                                              "subject": subject,
                                                                              "USER": supplier['name'],
                                                                              "BUYER_COMPANY_NAME": buyer_company_name,
                                                                              "LOT_NAME": data['lot']['lot_name'],
                                                                              "LINK_FOR_RFQ": rfq_link})
            p.start()

        # Confirmation Email to buyers

        return response.customResponse({"response": "Your RFQ has been created successfully and sent to the invited suppliers",
                                        "rfq_id": requisition_id})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/rfq/create", function_name="buyer_create_rfq()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for listing the RFQs for buyer
@app.route("/buyer/rfq/list", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_list():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        data['offset'] = data['offset'] if 'offset' in data else 0
        data['limit'] = data['limit'] if 'limit' in data else 5
        start_limit = data['offset']
        end_limit = data['offset'] + data['limit']
        cancelled = True if data['type'].lower() == "cancelled" else False
        requisitions = Join().get_buyer_requisitions(buyer_id=data['buyer_id'], start_limit=start_limit, end_limit=end_limit,
                                                     req_type=data['type'].lower(), cancelled=cancelled)
        # Looping through all the requisitions
        if len(requisitions) > 0:
            for req in requisitions:
                # Insert products and its documents
                req['products'] = Product().get_lot_products(req['lot_id'])
                if len(req['products']) > 0:
                    for prod in req['products']:
                        prod['documents'] = Document().get_docs(operation_id=prod['reqn_product_id'], operation_type="product")

                # Insert invited suppliers
                req['invited_suppliers'] = InviteSupplier().get_operation_suppliers_count(operation_id=req['requisition_id'],
                                                                                          operation_type="rfq")
                req['closes_on'] = GenericOps.calculate_closing_time(utc_deadline=req['utc_deadline'], op_tz=req['timezone'])
                # Insert number of responses received
                req['responses'] = Quotation().get_quotations_count_for_requisition(requisition_id=req['requisition_id'])
        join_obj = Join()
        count = {
            "open": join_obj.get_buyer_requisitions_count(buyer_id=data['buyer_id'], req_type="open"),
            "pending_approval": join_obj.get_buyer_requisitions_count(buyer_id=data['buyer_id'], req_type="pending_approval"),
            "approved": join_obj.get_buyer_requisitions_count(buyer_id=data['buyer_id'], req_type="approved"),
            "cancelled": join_obj.get_buyer_requisitions_count(buyer_id=data['buyer_id'], req_type="cancelled")
        }
        return response.customResponse({"requisitions": requisitions, "count": count})

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/list", function_name="buyer_create_list()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching the details of a RFQ
@app.route("/buyer/rfq/details/get", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_details_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        # Fetch the requisition details
        result = Requisition(data['requisition_id']).get_requisition()
        # Fetch the lot related to the requisition
        result['lot'] = Lot().get_lot_for_requisition(data['requisition_id'])
        # Fetch products and their documents
        result['products'] = Product().get_lot_products(result['lot']['lot_id'])
        # Fetch products documents
        for prod in result['products']:
            prod['documents'] = Document().get_docs(operation_id=prod['reqn_product_id'], operation_type="product")
        # Fetch specification documents
        result['specification_documents'] = Document().get_docs(operation_id=data['requisition_id'], operation_type="rfq")

        return response.customResponse({"rfq": result})

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/details/get", function_name="buyer_rfq_details_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching the suppliers quoting for the RFQ
@app.route("/buyer/rfq/suppliers/get", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_suppliers_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        suppliers = Join().get_suppliers_quoting(operation_id=data['requisition_id'], operation_type="rfq")
        return response.customResponse({"suppliers": suppliers})

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/suppliers/get", function_name="buyer_rfq_suppliers_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for managing supplier abilities in RFQ
@app.route("/buyer/rfq/suppliers/ops", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_supplier_ops():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buser = BUser(data['_id'])
        buyer_id = buser.get_buyer_id()
        buyer = Buyer(buyer_id)
        suser = SUser(supplier_id=data['supplier_id'])
        if data['operation_type'] == "unlock":
            if InviteSupplier().update_unlock_status(supplier_id=data['supplier_id'], operation_id=data['requisition_id'], operation_type="rfq", status=data['status']):
                ActivityLogs("").add_activity(activity="Unlock supplier", done_by=data['_id'], operation_id=data['requisition_id'],
                                              operation_type="rfq", type_of_user="buyer", user_id=buyer_id, ip_address=flask.request.remote_addr,
                                              name=buser.get_name(), company_name=buyer.get_company_name())
                suppliers = Join().get_suppliers_quoting(operation_id=data['requisition_id'], operation_type="rfq")
                lot = Lot().get_lot_for_requisition(requisition_id=data['requisition_id'])
                subject = conf.email_endpoints['buyer']['unlock_supplier']['subject'].replace("{{requisition_id}}", str(data['requisition_id']))
                link = conf.SUPPLIERS_ENDPOINT + conf.email_endpoints['buyer']['unlock_supplier']['page_url']
                p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [suser.get_email()],
                                                                                  "subject": subject,
                                                                                  "template": conf.email_endpoints['buyer']['unlock_supplier']['template_id'],
                                                                                  "USER": suser.get_first_name(),
                                                                                  "LOT_NAME": lot['lot_name'],
                                                                                  "BUYER_COMPANY_NAME": buyer.get_company_name(),
                                                                                  "RFQ_ID": str(data['requisition_id']),
                                                                                  "LINK": link})
                p.start()
                return response.customResponse({"response": "Supplier unlocked successfully", "suppliers": suppliers})
            return response.errorResponse("Oops, some error occured. Please try again after sometime")

        if data['operation_type'] == "remove":
            if InviteSupplier().remove_supplier(supplier_id=data['supplier_id'], operation_id=data['requisition_id'], operation_type="rfq"):
                suppliers = Join().get_suppliers_quoting(operation_id=data['requisition_id'], operation_type="rfq")
                # Remove Quotation
                quotation_ids = Quotation().get_quotation_ids(requisition_id=data['requisition_id'], supplier_id=data['supplier_id'])
                if len(quotation_ids) > 1:
                    for id in quotation_ids:
                        Quote().remove_quotes(quotation_id=id)
                        Quotation().remove_quotation(quotation_id=id)
                elif len(quotation_ids) == 1:
                    id = quotation_ids[0]
                    Quote().remove_quotes(quotation_id=id)
                    Quotation().remove_quotation(quotation_id=id)
                ActivityLogs("").add_activity(activity="Remove supplier", done_by=data['_id'],
                                              operation_id=data['requisition_id'],
                                              operation_type="rfq", type_of_user="buyer", user_id=buyer_id, ip_address=flask.request.remote_addr,
                                              name=buser.get_name(), company_name=buyer.get_company_name())
                return response.customResponse({"response": "Supplier removed from the RFQ successfully", "suppliers": suppliers})
            return response.errorResponse("Oops, some error occured. Please try again after sometime")

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/rfq/suppliers/ops", function_name="buyer_rfq_suppliers_ops()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for cancelling a RFQ
@app.route("/buyer/rfq/cancel", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_cancel():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buser = BUser(data['_id'])
        buyer_id = buser.get_buyer_id()
        buyer = Buyer(buyer_id)
        requisition = Requisition(data['requisition_id'])
        if requisition.cancel_rfq():
            ActivityLogs("").add_activity(activity="Cancel RFQ", done_by=data['_id'], operation_id=data['requisition_id'],
                                          operation_type="rfq", type_of_user="buyer", user_id=buyer_id, ip_address=flask.request.remote_addr,
                                          name=buser.get_name(), company_name=buyer.get_company_name())
            # Sending email to suppliers
            suppliers = Join().get_invited_suppliers(operation_id=data['requisition_id'], operation_type="rfq")
            lot = Lot().get_lot_for_requisition(requisition_id=data['requisition_id'])
            for supp in suppliers:
                p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [supp['email']],
                                                                                  "subject": conf.email_endpoints['buyer']['cancel_rfq']['subject'],
                                                                                  "template": conf.email_endpoints['buyer']['cancel_rfq']['template_id'],
                                                                                  "USER": supp['name'],
                                                                                  "RFQ_ID": str(data['requisition_id']),
                                                                                  "LOT_NAME": lot['lot_name'],
                                                                                  "BUYER_COMPANY_NAME": buyer.get_company_name()})
                p.start()
            return response.customResponse({"response": "RFQ: " + str(data['requisition_id']) + " has been cancelled successfully"})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/rfq/cancel", function_name="buyer_rfq_cancel()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for passing on the metadata about an RFQ
@app.route("/buyer/rfq/metadata", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_metadata():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        result = {}
        requisition = Requisition(data['requisition_id']).get_requisition()
        result['time_remaining'] = GenericOps.calculate_operation_deadline(utc_deadline=requisition['utc_deadline'])
        result['requisition_name'] = requisition['requisition_name']
        result['requisition_id'] = requisition['requisition_id']
        result['total_unread_messages'] = Message().get_total_unread_messages(operation_id=requisition['requisition_id'], operation_type="rfq_msg", receiver="buyer")
        result['responses'] = Quotation().get_quotations_count_for_requisition(requisition_id=requisition['requisition_id'])
        return response.customResponse({"details": result})

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/metadata", function_name="buyer_rfq_metadata()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for changing the deadline of an RFQ
@app.route("/buyer/rfq/deadline/change", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_deadline_change():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buser = BUser(data['_id'])
        buyer_id = buser.get_buyer_id()
        buyer = Buyer(buyer_id)
        requisition = Requisition(data['requisition_id'])
        deadline = GenericOps.get_calculated_timestamp(date_time=data['deadline'], op_tz=requisition.get_timezone())
        # Checking the deadline
        if GenericOps.get_current_timestamp_of_timezone(requisition.get_timezone()) + Implementations.deadline_change_time_factor > deadline:
            return response.errorResponse("Please set a deadline of more than 30 mins from the current time")
        utc_deadline = GenericOps.convert_datetime_to_utc_datetimestring(datetime_str=data['deadline'], op_tz=requisition.get_timezone())
        if requisition.update_deadline(deadline=deadline, utc_deadline=utc_deadline):
            time_remaining = GenericOps.calculate_operation_deadline(utc_deadline=requisition.get_utc_deadline())
            ActivityLogs("").add_activity(activity="Deadline changed", done_by=data['_id'], operation_id=data['requisition_id'],
                                          operation_type="rfq", type_of_user="buyer", user_id=buyer_id, ip_address=flask.request.remote_addr,
                                          name=buser.get_name(), company_name=buyer.get_company_name())
            suppliers = Join().get_invited_suppliers(operation_id=data['requisition_id'], operation_type="rfq")
            lot = Lot().get_lot_for_requisition(requisition_id=data['requisition_id'])
            subject= conf.email_endpoints['buyer']['change_in_deadline']['subject'].replace("{{requisition_id}}", str(data['requisition_id']))
            for supp in suppliers:
                p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [supp['email']],
                                                                                  "subject": subject,
                                                                                  "template": conf.email_endpoints['buyer']['change_in_deadline']['template_id'],
                                                                                  "USER": supp['name'],
                                                                                  "RFQ_ID": str(data['requisition_id']),
                                                                                  "LOT_NAME": lot['lot_name'],
                                                                                  "BUYER_COMPANY_NAME": buyer.get_company_name(),
                                                                                  "NEW_DEADLINE": data['deadline']})
                p.start()
            return response.customResponse({"response": "Deadline changed successfully", "time_remaining": time_remaining})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/rfq/deadline/change", function_name="buyer_rfq_deadline_change()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for inviting supplier(s) to quote against an RFQ
@app.route("/buyer/rfq/suppliers/invite", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_invite_supplier():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buser = BUser(data['_id'])
        buyer = Buyer(data['buyer_id'])
        suppliers = []
        for supplier in data['invited_suppliers']:
            if not InviteSupplier().is_supplier_present(supplier_id=supplier, operation_id=data['requisition_id'], operation_type="rfq"):
                supp = [data['requisition_id'], "rfq", supplier, GenericOps.get_current_timestamp(), True]
                supp = tuple(supp)
                suppliers.append(supp)
            else:
                del data['invited_suppliers'][data['invited_suppliers'].index(supplier)]

        # Adding multiple suppliers
        InviteSupplier("").insert_many(suppliers)
        # Adding in activity log
        ActivityLogs("").add_activity(activity="Invite supplier", done_by=data['_id'], operation_id=data['requisition_id'],
                                      operation_type="rfq",
                                      type_of_user="buyer", user_id=data['buyer_id'], ip_address=flask.request.remote_addr,
                                      name=buser.get_name(), company_name=buyer.get_company_name())
        # Fetching lot info for email notification
        lot = Lot().get_lot_for_requisition(requisition_id=data['requisition_id'])
        invited_suppliers = Join().get_invited_suppliers(operation_id=data['requisition_id'], operation_type="rfq")
        buyer_company_name = buyer.get_company_name()
        rfq_link = conf.SUPPLIERS_ENDPOINT + conf.email_endpoints['supplier']['rfq_created']['page_url']
        subject = conf.email_endpoints['supplier']['rfq_created']['subject'].replace("{{buyer_company}}", buyer_company_name).replace("{{lot_name}}", lot['lot_name'])
        if len(data['invited_suppliers']) > 0:
            for supplier in data['invited_suppliers']:
                suser = SUser(supplier_id=supplier)
                p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [suser.get_email()],
                                                                                  "template": conf.email_endpoints['supplier']['rfq_created']['template_id'],
                                                                                  "subject": subject,
                                                                                  "USER": suser.get_first_name(),
                                                                                  "BUYER_COMPANY_NAME": buyer_company_name,
                                                                                  "LOT_NAME": lot['lot_name'],
                                                                                  "LINK_FOR_RFQ": rfq_link})
                p.start()

        return response.customResponse({"suppliers": invited_suppliers, "response": "Supplier(s) invited successfully"})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/rfq/suppliers/invite", function_name="buyer_rfq_invite_supplier()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching the quotes received form the suppliers
@app.route("/buyer/rfq/quotes/get", methods=["POST"])
@validate_buyer_access_token
def get_buyer_rfq_quotes():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        lot = Lot().get_lot_for_requisition(requisition_id=data['requisition_id'])
        # If no lot is found
        if len(lot) == 0:
            return response.errorResponse("No lot found against this RFQ")
        invited_suppliers = Join().get_suppliers_quoting(operation_id=data['requisition_id'], operation_type="rfq")
        # If no suppliers are quoting
        if len(invited_suppliers) == 0:
            return response.errorResponse("No suppliers are quoting against this RFQ")
        products = Product().get_lot_products(lot_id=lot['lot_id'])
        if len(products) > 0:
            for i in range(0, len(products)):
                products[i]['quotes'] = Quote().get_supplier_quotes_for_requisition(requisition_id=data['requisition_id'],
                                                                                    charge_id=products[i]['reqn_product_id'])

                # Setting the is_confirmed key for a product
                products[i]['is_confirmed'] = Quote().is_product_quote_confirmed(charge_id=products[i]['reqn_product_id'])
            return response.customResponse({"quotes_received": products, "suppliers": invited_suppliers})
        return response.errorResponse("No products found in this lot")

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/quotes/get", function_name="get_buyer_rfq_quotes()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching the CFO quotes out of all the received ones
@app.route("/buyer/rfq/quotes/summary", methods=["POST"])
@validate_buyer_access_token
def get_buyer_rfq_quotes_summary():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        lot = Lot().get_lot_for_requisition(requisition_id=data['requisition_id'])
        # If no lot is found
        if len(lot) == 0:
            return response.errorResponse("No lot found against this RFQ")
        invited_suppliers = Join().get_suppliers_quoting(operation_id=data['requisition_id'], operation_type="rfq")
        # If no suppliers are quoting
        if len(invited_suppliers) == 0:
            return response.errorResponse("No suppliers are quoting against this RFQ")
        products = Product().get_lot_products(lot_id=lot['lot_id'])
        if len(products) > 0:
            quote = Quote()
            optimal_total, cheapest_total, fastest_total = 0, 0, 0
            qt_not_found_counter = 0
            for i in range(0, len(products)):
                # Setting the is_confirmed key for a product
                products[i]['is_confirmed'] = Quote().is_product_quote_confirmed(charge_id=products[i]['reqn_product_id'])

                # Fetching the cheapest and optimal rates
                products[i]['cheapest'] = quote.get_quotes_by_category(requisition_id=data['requisition_id'], charge_id=products[i]['reqn_product_id'])
                products[i]['fastest'] = quote.get_quotes_by_category(requisition_id=data['requisition_id'], charge_id=products[i]['reqn_product_id'], category="fastest")
                products[i]['optimal'] = []
                if len(products[i]['cheapest']) == 0 or len(products[i]['fastest']) == 0:
                    qt_not_found_counter += 1
                    continue
                # Fetching and calculating the optimal rates
                cheapest_amount, fastest_time = products[i]['cheapest']['amount'], products[i]['fastest']['delivery_time']
                optimal = quote.get_supplier_quotes_for_requisition(requisition_id=data['requisition_id'], charge_id=products[i]['reqn_product_id'])
                amount_deviations, delivery_deviations = [], []
                # calculating deviations
                for obj in optimal:
                    amount_deviations.append(obj['amount'] - cheapest_amount)
                    delivery_deviations.append(obj['delivery_time'] - fastest_time)
                # Standardizing the deviations calculated
                std_amount_deviations, std_max_del_deviation = [], []
                max_amount_deviation, max_delivery_deviation = max(amount_deviations), max(delivery_deviations)
                for x in amount_deviations:
                    if max_amount_deviation != 0:
                        std_amount_deviations.append(x/max_amount_deviation)
                    else:
                        std_amount_deviations.append(0)
                for x in delivery_deviations:
                    if max_delivery_deviation != 0:
                        std_max_del_deviation.append(x/max_delivery_deviation)
                    else:
                        std_max_del_deviation.append(0)
                # Finding the optimal choice
                sum_deviations = std_amount_deviations + std_max_del_deviation
                optimal_choice_ind = sum_deviations.index(min(sum_deviations))
                products[i]['optimal'] = optimal[optimal_choice_ind]
                # Calculating totals for the 3 categories
                optimal_total += products[i]['optimal']['amount']
                cheapest_total += products[i]['cheapest']['amount']
                fastest_total += products[i]['fastest']['amount']
            # If no quotes are available
            if qt_not_found_counter <= len(products):
                return response.customResponse({"summary": products,
                                                "optimal_total": GenericOps.round_of(optimal_total),
                                                "cheapest_total": GenericOps.round_of(cheapest_total),
                                                "fastest_total": GenericOps.round_of(fastest_total)})
            # If quotes are available
            return response.customResponse({"summary": products,
                                            "optimal_total": GenericOps.round_of(optimal_total),
                                            "cheapest_total": GenericOps.round_of(cheapest_total),
                                            "fastest_total": GenericOps.round_of(fastest_total)})
        return response.errorResponse("No products found in this lot")

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/quotes/summary", function_name="get_buyer_rfq_quotes_summary()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for downloading excel of quotations received
@app.route("/buyer/rfq/quotes/download", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_quotes_download():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        return response.customResponse({"base64": Reports(operation_id=data['requisition_id']).generate_all_quotations_report(),
                                        "response": "Your requested file will be downloaded shortly"})

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/quotes/download", function_name="buyer_rfq_quotes_download()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### SUPPLIER RFQ SECTION #####################################################

# POST request for listing the RFQs for buyer
@app.route("/supplier/quotation/send", methods=["POST"])
@validate_supplier_access_token
def supplier_quotation_send():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        quotation = data['quotation']
        suser = SUser(data['_id'])
        supplier_id = suser.get_supplier_id()
        requisition = Requisition(data['requisition_id'])
        supplier = Supplier(supplier_id)
        unlock_status = InviteSupplier().get_unlock_status(supplier_id=supplier_id, operation_id=data['requisition_id'],
                                                           operation_type="rfq")

        # Applied the logic of submission limit in a rfq
        quotation_count = Quotation().get_supplier_quotation_count(requisition_id=data['requisition_id'], supplier_id=supplier_id)
        submission_limit = requisition.get_submission_limit()

        if requisition.get_cancelled():
            return response.errorResponse("You cannot quote against a cancelled RFQ")

        # Checking the unlock status
        if not unlock_status:
            return response.errorResponse("You cannot quote more than once until buyer unlocks you to quote from his dashboard")

        # If supplier is quoting for a closed RFQ
        if requisition.get_request_type() != "open":
            return response.errorResponse("This RFQ is not accepting any further quotations from suppliers")

        # Add quotation
        quotation_id = Quotation().add_quotation(supplier_id=suser.get_supplier_id(), requisition_id=data['requisition_id'],
                                                 total_amount=quotation['total_amount'],
                                                 total_gst=quotation['total_gst'], quote_validity=quotation['quote_validity'])


        # Add quotes
        quotes = []
        for quote in quotation['quotes']:
            qt = [quotation_id, quote['charge_id'], quote['charge_name'], quote['quantity'], quote['gst'],
                  quote['per_unit'], quote['amount'], quote['delivery_time'], False]
            qt = tuple(qt)
            quotes.append(qt)
        quotes_id = Quote().insert_many(quotes)

        if not quotation_id or not quotes_id:
            return response.errorResponse("Failed to send quotation, please try again")

        # Update the unlock_status of supplier
        if submission_limit <= quotation_count + 1 and unlock_status:
            InviteSupplier().update_unlock_status(supplier_id=supplier_id, operation_id=data['requisition_id'], operation_type="rfq", status=False)

        ActivityLogs("").add_activity(activity="Quotation sent", done_by=data['_id'],
                                      operation_id=data['requisition_id'],
                                      operation_type="rfq",
                                      type_of_user="supplier", user_id=supplier_id, ip_address=flask.request.remote_addr,
                                      name=suser.get_name(), company_name=supplier.get_company_name())
        # Sending a mail to buyer
        supplier_company_name = supplier.get_company_name()
        buyers = Join().get_buyers_for_rfq(data['requisition_id'])
        subject = conf.email_endpoints['supplier']['quotation_submitted']['subject'].replace("{{supplier_company_name}}", supplier_company_name).replace("{{requisition_id}}", str(data['requisition_id']))
        link = conf.ENV_ENDPOINT + conf.email_endpoints['supplier']['quotation_submitted']['page_url'].replace("{{requisition_id}}", str(data['requisition_id']))
        for buyer in buyers:
            p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [buyer['email']],
                                                                              "template": conf.email_endpoints['supplier']['quotation_submitted']['template_id'],
                                                                              "subject": subject,
                                                                              "USER": buyer['name'],
                                                                              "SUPPLIER_NAME": supplier_company_name,
                                                                              "TYPE_OF_REQUEST": "RFQ",
                                                                              "REQUEST_ID": str(data['requisition_id']),
                                                                              "LOT_NAME": buyer['requisition_name'],
                                                                              "LINK": link})
            p.start()

        # Sending unlock status for handling UI
        unlock_status = InviteSupplier().get_unlock_status(supplier_id=supplier_id, operation_id=data['requisition_id'],
                                                           operation_type="rfq")

        submissions_left = submission_limit - (quotation_count + 1) if quotation_count <= submission_limit else 0
        return response.customResponse({"response": "Quotation sent successfully", "unlock_status": unlock_status,
                                        "submissions_left": submissions_left})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/supplier/quotation/send", function_name="supplier_quotation_send()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for listing the RFQs for supplier
@app.route("/supplier/rfq/list", methods=["POST"])
@validate_supplier_access_token
def supplier_rfq_list():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        data['offset'] = data['offset'] if 'offset' in data else 0
        data['limit'] = data['limit'] if 'limit' in data else 5
        start_limit = data['offset']
        end_limit = data['offset'] + data['limit']
        cancelled = True if data['type'].lower() == "cancelled" else False
        requisitions = Join().get_supplier_requisitions(supplier_id=data['supplier_id'], start_limit=start_limit, end_limit=end_limit,
                                                        req_type=data['type'].lower(), cancelled=cancelled)
        # Looping through all the requisitions
        if len(requisitions) > 0:
            for req in requisitions:
                # Insert products and its documents
                req['products'] = Product().get_lot_products(req['lot_id'])
                req['time_remaining'] = GenericOps.calculate_operation_deadline(utc_deadline=req['utc_deadline'])
                req['unread_messages'] = Message().get_unread_messages(operation_id=req['requisition_id'], operation_type="rfq",
                                                                       receiver_id=data['supplier_id'], receiver_type="supplier",
                                                                       sender="buyer", sent_by=req['buyer_id'])

                quotation_count = Quotation().get__supplier_quotations_count_for_requisition(requisition_id=req['requisition_id'],
                                                                                             supplier_id=data['supplier_id'])
                req['submissions_left'] = req['submission_limit'] - quotation_count if quotation_count <= req['submission_limit'] else 0
                if len(req['products']) > 0:
                    for prod in req['products']:
                        prod['documents'] = Document().get_docs(operation_id=prod['reqn_product_id'], operation_type="product")

                # Insert specification docs
                req['specification_documents'] = Document().get_docs(operation_id=req['requisition_id'], operation_type="rfq")
        join_obj = Join()
        count = {
            "open": join_obj.get_supplier_requisitions_count(supplier_id=data['supplier_id'], req_type="open"),
            "pending_approval": join_obj.get_supplier_requisitions_count(supplier_id=data['supplier_id'], req_type="pending_approval"),
            "approved": join_obj.get_supplier_requisitions_count(supplier_id=data['supplier_id'], req_type="approved"),
            "cancelled": join_obj.get_supplier_requisitions_count(supplier_id=data['supplier_id'], req_type="cancelled")
        }
        return response.customResponse({"requisitions": requisitions, "count": count})

    except Exception as e:
        log = Logger(module_name="/supplier/rfq/list", function_name="supplier_rfq_list()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching the last quote and rank of supplier according to products
@app.route("/supplier/rfq/last-quote/get", methods=["POST"])
@validate_supplier_access_token
def supplier_rfq_last_quote_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        lot = Lot().get_lot_for_requisition(requisition_id=data['requisition_id'])
        # If no lot is found
        if len(lot) == 0:
            return response.errorResponse("No lot found against this RFQ")
        products = Product().get_lot_products(lot_id=lot['lot_id'])
        if len(products) > 0:
            result = []
            for i in range(0, len(products)):
                quotes = Quote().get_supplier_quotes_for_requisition(requisition_id=data['requisition_id'],
                                                                                    charge_id=products[i]['reqn_product_id'])

                # Getting rank of the supplier
                for i in range(0, len(quotes)):
                    if quotes[i]['supplier_id'] == data['supplier_id']:
                        quotes[i]['rank'] = i+1
                        products[i]['quote'] = quotes[i]
                if 'quote' not in products[i]:
                    products[i]['quote'] = {}
                result.append(products[i])
            return response.customResponse({"products": result})
        return response.errorResponse("No products found in this lot")

    except Exception as e:
        log = Logger(module_name="/supplier/rfq/last-quote/get", function_name="supplier_rfq_last_quote_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### MESSAGE SECTION ##########################################################

# POST request for sending a message
@app.route("/message/send", methods=['POST'])
@validate_access_token
def send_message():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        type_of_request = data['operation_type'].split("_")[0].upper()
        # Insert the documents
        documents, document_ids = [], []

        message_id = Message().add_message(operation_id=data['operation_id'], operation_type=data['operation_type'],
                                           message=data['message'], sender_user=data['_id'],
                                           sent_by=data['client_id'], sender=data['client_type'], received_by=data['receiver_id'],
                                           receiver=data['receiver_type'])

        if len(data['documents']) > 0:
            for document in data['documents']:
                doc = [message_id, data['operation_type'], data['operation_id'], document['document_url'], document['document_type'],
                       document['document_name'], document['uploaded_on'], data['_id'], data['client_type']]
                doc = tuple(doc)
                documents.append(doc)
            document_ids += MessageDocument().insert_many(documents)

        # Sending emails on message send
        if data['client_type'].lower() == "buyer":
            buyer = Buyer(data['client_id'])
            buser = BUser(data['_id'])
            suser = SUser(supplier_id=data['receiver_id'])
            subject = conf.email_endpoints['supplier']['message_received']['subject'].replace("{{requisition_id}}", str(data['operation_id'])).replace("{{operation_type}}", type_of_request)
            link = conf.SUPPLIERS_ENDPOINT + conf.email_endpoints['supplier']['message_received']['page_url'].replace("{{operation}}", type_of_request.lower())
            lot = Lot().get_lot_for_requisition(requisition_id=data['operation_id'])
            sender = buser.get_name() + " (" + buyer.get_company_name() + ")"
            p = Process(target=EmailNotifications.send_message_email, kwargs={"recipients": [suser.get_email()],
                                                                              "template": conf.email_endpoints['supplier']['message_received']['template_id'],
                                                                              "subject": subject,
                                                                              "LINK_FOR_REPLY": link,
                                                                              "USER": suser.get_first_name(),
                                                                              "TYPE_OF_REQUEST": type_of_request,
                                                                              "REQUEST_ID": str(data['operation_id']),
                                                                              "LOT_NAME": lot['lot_name'],
                                                                              "SENDER": sender,
                                                                              "MESSAGE": data['message'],
                                                                              "documents": data['documents']})
            p.start()
        else:
            supplier = Supplier(data['client_id'])
            suser = SUser(data['_id'])
            busers = BUser().get_busers_for_buyer_id(buyer_id=data['receiver_id'])
            subject = conf.email_endpoints['buyer']['message_received']['subject'].replace("{{requisition_id}}", str(data['operation_id'])).replace("{{operation_type}}", type_of_request)
            link = conf.ENV_ENDPOINT + conf.email_endpoints['buyer']['message_received']['page_url'].replace("{{operation}}", type_of_request.lower()).replace("{{action_type}}", "quotes").replace("{{operation_id}}", str(data['operation_id']))
            lot = Lot().get_lot_for_requisition(requisition_id=data['operation_id'])
            sender = suser.get_name() + " (" + supplier.get_company_name() + ")"
            for user in busers:
                p = Process(target=EmailNotifications.send_message_email, kwargs={"recipients": [user['email']],
                                                                                  "subject": subject,
                                                                                  "template": conf.email_endpoints['buyer']['message_received']['template_id'],
                                                                                  "LINK_FOR_REPLY": link,
                                                                                  "USER": user['name'].split(" ")[0],
                                                                                  "TYPE_OF_REQUEST": type_of_request,
                                                                                  "REQUEST_ID": str(data['operation_id']),
                                                                                  "LOT_NAME": lot['lot_name'],
                                                                                  "SENDER": sender,
                                                                                  "MESSAGE": data['message'],
                                                                                  "documents": data['documents']})
                p.start()

        message = Message(message_id).get_message()
        message['documents'] = data['documents']
        return response.customResponse({"response": "Message sent successfully", "message": message})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/message/send", function_name="send_message()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching messages
@app.route("/messages/suppliers/get", methods=['POST'])
@validate_access_token
def messages_suppliers_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if data['client_type'] == "buyer":
            operation_type = data['operation_type'].split("_")[0]

            suppliers = Join().get_suppliers_messaging(operation_id=data['operation_id'], operation_type=operation_type)
            for supp in suppliers:
                supp['unread_messages'] = Message().get_unread_messages(operation_id=data['operation_id'], operation_type=data['operation_type'],
                                                                            sent_by=supp['supplier_id'], sender="supplier",
                                                                            receiver_id=data['client_id'], receiver_type=data['client_type'])

                last_message = Message().get_last_message(operation_id=data['operation_id'], operation_type=data['operation_type'],
                                                                            sent_by=data['client_id'], sender=data['client_type'],
                                                                            receiver_id=supp['supplier_id'], receiver_type="supplier")

                if last_message is not None:
                    supp['last_message'] = last_message['message']
                    supp['last_message_timestamp'] = last_message['sent_on']
                else:
                    supp['last_message'] = ""
                    supp['last_message_timestamp'] = 0

            return response.customResponse({"suppliers": suppliers})

    except Exception as e:
        log = Logger(module_name="/messages/suppliers/get", function_name="messages_suppliers_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching messages
@app.route("/messages/receive", methods=['POST'])
@validate_access_token
def receive_messages():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        data['offset'] = data['offset'] if 'offset' in data else 0
        data['limit'] = data['limit'] if 'limit' in data else 10
        start_limit = data['offset']
        end_limit = data['offset'] + data['limit']
        messages = Message().get_operation_messages(operation_id=data['operation_id'], operation_type=data['operation_type'],
                                                    sent_by=data['client_id'], sender=data['client_type'],
                                                    receiver_id=data['receiver_id'], receiver_type=data['receiver_type'],
                                                    start_limit=start_limit, end_limit=end_limit)
        if len(messages) > 0:
            for msg in messages:
                msg['documents'] = MessageDocument().get_message_docs(operation_id=msg['message_id'], operation_type=data['operation_type'])

        return response.customResponse({"messages": messages})

    except Exception as e:
        log = Logger(module_name="/messages/receive", function_name="receive_messages()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for marking messages as read
@app.route("/messages/read", methods=['POST'])
@validate_access_token
def read_messages():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        Message().read_messages(operation_id=data['operation_id'], operation_type=data['operation_type'],
                                sent_by=data['receiver_id'], sender=data['receiver_type'],
                                receiver_id=data['client_id'], receiver_type=data['client_type'])

        return response.customResponse({"read_flag": True, "response": "Messages read successfully"})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/messages/read", function_name="read_messages()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching messages
@app.route("/messages/documents/get", methods=['POST'])
@validate_access_token
def get_messages_documents():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        documents = MessageDocument().get_docs(entity_id=data['operation_id'], operation_type=data['operation_type'])
        return response.customResponse({"documents": documents})

    except Exception as e:
        log = Logger(module_name="/messages/documents/get", function_name="get_messages_documents()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### CONTACT SECTION ##########################################################

# POST request for sending contact details to identex team
@app.route("/request/demo", methods=["POST"])
def contact_details_submit():
    try:
        data = request.json
        if data['request_type'].lower() == "free_trial":
            msg = "<h3>" + data['email'] + "</h3> has requested for a free trial."
            p = Process(target=EmailNotifications.send_mail, kwargs={"subject": "Request for a free trial",
                                                                     "recipients": [conf.default_founder_email],
                                                                     "message": msg})
            p.start()
            return response.customResponse({"response": "Thank you, someone, from our team will contact you shortly"})
        if data['request_type'].lower() == "demo":
            msg = "Name: " + data['name'] + "<br>Company Name: " + data['company_name'] + "<br>Email: " + data['email'] + "<br>Mobile Number: " + data['mobile_no'] + "<br>Country: " + data['country'] + "<br>Additional Comments: " + data['additional_comments']
            subject = "Request for a demo from " + data['company_name'] + " (" + data['name'] + ")"
            p = Process(target=EmailNotifications.send_mail, kwargs={"subject": subject,
                                                                     "message": msg,
                                                                     "recipients": [conf.default_founder_email]})
            p.start()
            return response.customResponse({"response": "Thank you, someone, from our team will contact you shortly"})
        return response.errorResponse("Invalid request type")

    except Exception as e:
        log = Logger(module_name="/contact-details/submit", function_name="contact_details_submit()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### SUPPLIERS SECTION #########################################################

# POST request for adding/inviting suppliers
@app.route("/buyer/supplier/add", methods=['POST'])
@validate_buyer_access_token
def buyer_supplier_add():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buser = BUser(data['_id'])
        buyer_id = buser.get_buyer_id()
        suppliers = data['supplier_details']
        for supp in suppliers:
            supp['email'] = supp['email'].lower()

            # If supplier is present
            if SUser.is_suser(supp['email']):
                suser = SUser(supp['email'])
                SupplierRelationship().add_supplier_relationship(buyer_id, suser.get_supplier_id())
                # Send an email to supplier
                p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [supp['email']],
                                                                                  "template": conf.email_endpoints['buyer']['supplier_onboarding']['template_id'],
                                                                                  "subject": conf.email_endpoints['buyer']['supplier_onboarding']['subject'],
                                                                                  "SUPPLIER_USER": suser.get_first_name(),
                                                                                  "BUYER_COMPANY_NAME": Buyer(buyer_id).get_company_name(),
                                                                                  "FIRST_INVITE": "none"})
                p.start()
            # If supplier is not present
            else:
                supplier_id = Supplier().add_supplier(company_name=supp['company_name'])
                password = GenericOps.generate_user_password()
                SUser().add_suser(email=supp['email'], name=supp['name'], supplier_id=supplier_id, password=hashlib.sha1(password.encode()).hexdigest())
                SupplierRelationship().add_supplier_relationship(buyer_id, supplier_id)
                # Send an email to supplier
                suser = SUser(supp['email'])
                p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [supp['email']],
                                                                                  "template": conf.email_endpoints['buyer']['supplier_onboarding']['template_id'],
                                                                                  "subject": conf.email_endpoints['buyer']['supplier_onboarding']['subject'],
                                                                                  "SUPPLIER_USER": suser.get_first_name(),
                                                                                  "BUYER_COMPANY_NAME": Buyer(buyer_id).get_company_name(),
                                                                                  "SUPPLIER_USERNAME": suser.get_email(),
                                                                                  "PASSWORD": password,
                                                                                  "FIRST_INVITE": "block"})
                p.start()

        result = Join().get_suppliers_info(buyer_id)
        return response.customResponse({"response": "Supplier(s) added successfully",
                                        "suppliers": result})

    except Exception as e:
        log = Logger(module_name='/buyer/supplier/add', function_name='buyer_supplier_add()')
        log.log(traceback.format_exc(), priority='highest')
        return response.errorResponse("Some error occurred please try again later")

# POST request for fetching list of suppliers for buyer
@app.route("/buyer/suppliers/get", methods=["POST"])
@validate_buyer_access_token
def buyer_suppliers_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buyer_id = BUser(data['_id']).get_buyer_id()
        suppliers = Join().get_suppliers_info(buyer_id=buyer_id)
        return response.customResponse({"suppliers": suppliers})

    except Exception as e:
        log = Logger(module_name="/buyer/suppliers/get", function_name="buyer_suppliers_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for deleting suppliers (parked for now)
@app.route("/buyer/suppliers/delete", methods=["POST"])
@validate_buyer_access_token
def buyer_suppliers_delete():
    try:
        pass

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/suppliers/delete", function_name="buyer_suppliers_delete()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### PRODUCTS SECTION ##########################################################

# POST request for fetching list of products for buyer
@app.route("/buyer/products/get", methods=["POST"])
@validate_buyer_access_token
def buyer_products_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        products = ProductMaster().get_buyer_products(buyer_id=data['buyer_id'])
        return response.customResponse({"products": products})

    except Exception as e:
        log = Logger(module_name="/buyer/products/get", function_name="buyer_products_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for adding new products to the product master of buyer
@app.route("/buyer/product/add", methods=["POST"])
@validate_buyer_access_token
def buyer_product_add():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        # Check whether the product is existing or not
        if not ProductMaster().is_product_added(product_name=data['product_name'].lower(),
                                                product_category=data['product_category'].lower(),
                                                buyer_id=data['buyer_id']):
            # Insert the product
            product_id = ProductMaster().add_product(product_name=data['product_name'], product_category=data['product_category'],
                                                     buyer_id=data['buyer_id'])
            return response.customResponse({"response": "Product added successfully", "product_id": product_id})
        return response.errorResponse("Product already exists in the inventory. Please select it from the products dropdown")

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/product/add", function_name="buyer_product_add()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for editing/deleting a buyer product
@app.route("/buyer/products/modify", methods=["POST"])
@validate_buyer_access_token
def buyer_products_modify():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        if not data['truncate']:
            ProductMaster(data['product_id']).update_product_details(values=data)
            return response.customResponse({"response": "Product details updated successfully",
                                            "product_id": data['product_id'],
                                            "product_name": data['product_name'],
                                            "product_category": data['product_category']})
        else:
            ProductMaster(data['product_id']).delete_product()
            return response.customResponse({"response": "Product deleted successfully"})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/products/modify", function_name="buyer_products_modify()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### ORDERS SECTION ############################################################

# POST request for adding orders
@app.route("/buyer/order/create", methods=['POST'])
@validate_buyer_access_token
def buyer_order_create():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        details = data['details']
        if details['acquisition_type'].lower() == "rfq":
            requisition = Requisition(details['acquisition_id'])
            lot = Lot().get_lot_for_requisition(requisition_id=details['acquisition_id'])
            # If no lot is found
            if len(lot) == 0:
                return response.errorResponse("No lot found against this RFQ")
            products = Product().get_lot_products(lot_id=lot['lot_id'])

            if len(products) > 0:
                approved_counter = 0
                # Iterate over the products
                for i in range(0, len(products)):
                    # Check whether the product is confirmed or not
                    product_confirmed = Quote().is_product_quote_confirmed(charge_id=products[i]['reqn_product_id'])
                    if product_confirmed:
                        approved_counter += 1

                # Create an order for the product if not
                order_created = Order().add_order(buyer_id=data['buyer_id'], supplier_id=details['supplier_id'],
                                                  po_no=details['po_no'],
                                                  acquisition_id=details['acquisition_id'],
                                                  acquisition_type=details['acquisition_type'],
                                                  quote_id=details['quote_id'],
                                                  reqn_product_id=details['reqn_product_id'],
                                                  remarks=details['remarks'])
                # Mark the particular quote as confirmed
                if order_created:
                    Quote(details['quote_id']).set_confirmed(True)
                    approved_counter += 1
                # If all the products are ordered then set the requisition status as approved
                if approved_counter == len(products):
                    requisition.set_request_type(request_type="approved")
                    requisition.drop_sql_event()
                # Email to supplier

                return response.customResponse({"response": "Order created successfully"})
            return response.errorResponse("No products found in this lot")
        return response.errorResponse("Invalid acquisition type")

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/order/create", function_name="buyer_order_create()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for listing orders for buyer
@app.route("/buyer/orders/get", methods=['POST'])
@validate_buyer_access_token
def buyer_orders_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['offset'] = data['offset'] if 'offset' in data else 0
        data['limit'] = data['limit'] if 'limit' in data else 5
        start_limit = data['offset']
        end_limit = data['offset'] + data['limit']
        orders =  Order().get_orders(client_id=data['buyer_id'], client_type="buyer",
                                     request_type=data['type'].lower(), start_limit=start_limit, end_limit=end_limit)

        # Fetching the orders count for different categories
        join_obj = Join()
        count = {
            "active": join_obj.get_buyer_orders_count(buyer_id=data['buyer_id'], req_type="active"),
            "delivered": join_obj.get_buyer_orders_count(buyer_id=data['buyer_id'], req_type="delivered"),
            "cancelled": join_obj.get_buyer_orders_count(buyer_id=data['buyer_id'], req_type="cancelled")
        }
        return response.customResponse({"orders": orders, "count": count})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/orders/get", function_name="buyer_orders_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for listing orders for supplier
@app.route("/supplier/orders/get", methods=['POST'])
@validate_supplier_access_token
def supplier_orders_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['offset'] = data['offset'] if 'offset' in data else 0
        data['limit'] = data['limit'] if 'limit' in data else 5
        start_limit = data['offset']
        end_limit = data['offset'] + data['limit']
        orders = Order().get_orders(client_id=data['supplier_id'], client_type="supplier", request_type=data['type'].lower(),
                                    start_limit=start_limit, end_limit=end_limit)
        for order in orders:
            if order['grn_uploaded']:
                order['grn_url'] = Document().get_order_docs_url(operation_id=order['order_id'], operation_type="order")

        # Fetching the orders count for different categories
        join_obj = Join()
        count = {
            "active": join_obj.get_supplier_orders_count(supplier_id=data['supplier_id'], req_type="active"),
            "delivered": join_obj.get_supplier_orders_count(supplier_id=data['supplier_id'], req_type="delivered"),
            "cancelled": join_obj.get_supplier_orders_count(supplier_id=data['supplier_id'], req_type="cancelled")
        }
        return response.customResponse({"orders": orders, "count": count})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/supplier/orders/get", function_name="supplier_orders_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for cancelling an order
@app.route("/buyer/order/cancel", methods=['POST'])
@validate_buyer_access_token
def buyer_order_cancel():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        order = Order(data['order_id'])
        quote_id = order.get_quote_id()
        quote = Quote(quote_id)
        if quote.set_confirmed(confirmed=False):
            order.set_order_status(order_status="cancelled")
            # Email to supplier
            return response.customResponse({"response": "Order cancelled successfully"})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/order/cancel", function_name="buyer_order_cancel()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for uploading GRN against an order
@app.route("/buyer/order/grn/upload", methods=['POST'])
@validate_buyer_access_token
def buyer_order_grn_upload():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        order = Order(data['order_id'])

        # If GRN copy is uploaded
        if len(data['documents']) > 0:
            documents, document_ids = [], []
            for document in data['documents']:
                doc = [data['order_id'], "order", document['document_url'], "grn", document['document_name'],
                       document['uploaded_on'], data['_id'], "buyer"]
                doc = tuple(doc)
                documents.append(doc)
            document_ids += Document("").insert_many(documents)

        # Update the status of grn_uploaded in orders table
        grn_uploaded = order.set_grn_uploaded(grn_uploaded=True)
        delivery_date_ts = GenericOps.convert_datestring_to_timestamp(data['delivery_date'])
        delivery_date = order.set_delivery_date(delivery_date=delivery_date_ts)
        order_status = order.set_order_status(order_status="delivered")
        # Success response
        if grn_uploaded and delivery_date and order_status:
            # Email to supplier
            return response.customResponse({"response": "GRN uploaded successfully", "grn_uploaded": order.get_grn_uploaded()})

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/order/grn/upload", function_name="buyer_order_grn_upload()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for updating payment status of an order
@app.route("/buyer/order/payment-status/update", methods=['POST'])
@validate_buyer_access_token
def buyer_order_payment_status_update():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        order = Order(data['order_id'])
        if data['payment_status']:
            payment_status = order.set_payment_status(payment_status="paid")
            transaction_ref_no = order.set_transaction_ref_no(transaction_ref_no=data['transaction_ref_no'])
            payment_date_ts = GenericOps.convert_datestring_to_timestamp(data['payment_date'])
            payment_date = order.set_payment_date(payment_date=payment_date_ts)
            if payment_status and transaction_ref_no and payment_date:
                # Email to supplier
                return response.customResponse({"response": "Order payment status updated successfully",
                                                "payment_status": order.get_payment_status(),
                                                "payment_date": order.get_payment_date(),
                                                "transaction_ref_no": order.get_transaction_ref_no()})
        return response.errorResponse("Invalid payment status")

    except exceptions.IncompleteRequestException as e:
        return response.errorResponse(e.error)
    except Exception as e:
        log = Logger(module_name="/buyer/order/payment-status/update", function_name="buyer_order_payment_status_update()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### MISCELLANEOUS SECTION #####################################################

# POST request for fetching messages
@app.route("/activity-logs/get", methods=['POST'])
@validate_access_token
def get_activity_logs():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        data['offset'] = data['offset'] if 'offset' in data else 0
        data['limit'] = data['limit'] if 'limit' in data else 15
        start_limit = data['offset']
        end_limit = data['offset'] + data['limit']
        activity_logs = ActivityLogs().get_activity_logs(type_of_user="buyer", user_id=data['client_id'], start_limit=start_limit,
                                                         end_limit=end_limit)
        return response.customResponse({"activity_logs": activity_logs})

    except Exception as e:
        log = Logger(module_name="/activity-logs/get", function_name="get_activity_logs()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching supplier operations count
@app.route("/supplier-operations/count", methods=['POST'])
@validate_supplier_access_token
def supplier_operations_count():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        count = {}
        join = Join()
        count['open_requisitions_count'] = join.get_supplier_requisitions_count(supplier_id=data['supplier_id'], req_type="open", operation_type="rfq")
        count['active_orders_count'] = join.get_supplier_orders_count(supplier_id=data['supplier_id'], req_type="active")
        return response.customResponse({"operations_count": count})

    except Exception as e:
        log = Logger(module_name="/supplier-operations/count", function_name="supplier_operations_count()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching buyer operations count
@app.route("/buyer-operations/count", methods=['POST'])
@validate_buyer_access_token
def buyer_operations_count():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        count = {}
        join = Join()
        count['open_requisitions_count'] = join.get_buyer_requisitions_count(buyer_id=data['buyer_id'], req_type="open")
        count['active_orders_count'] = join.get_buyer_orders_count(buyer_id=data['buyer_id'], req_type="active")
        return response.customResponse({"operations_count": count})

    except Exception as e:
        log = Logger(module_name="/buyer-operations/count", function_name="buyer_operations_count()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, threaded=True)