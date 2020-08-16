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
            for token in active_tokens:
                Authorization(token['_id']).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="password_reset")
                DBConnectivity.delete_redis_key(token['_id'])
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
            for token in active_tokens:
                Authorization(token['_id']).logout_user(logged_out=GenericOps.get_current_timestamp(), action_type="password_reset")
                DBConnectivity.delete_redis_key(token['_id'])
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
                                                "_id": data['_id'],
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
        pprint(request.json)
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buyer_id = data['buyer_id']
        buyer = Buyer(buyer_id)
        if len(data['invited_suppliers']) == 0:
            return response.errorResponse("Please invite atleast one supplier in order to create RFQ")

        if len(data['products']) == 0:
            return response.errorResponse("Please add atleast one product in order to create RFQ")

        document_ids, product_ids, invited_suppliers_ids = [], [], []
        pprint(data)
        # Create the requisition
        deadline = GenericOps.get_calculated_timestamp(data['deadline'])
        requisition_id = Requisition("").add_requisition(requisition_name=data['lot']['lot_name'], timezone=data['timezone'],
                                                         currency=data['currency'], buyer_id=buyer_id, deadline=deadline)
        pprint(requisition_id)
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
        product_ids = []
        for product in data['products']:
            product_id = Product("").add_product(lot_id=lot_id, buyer_id=buyer_id, product_name=product['product_name'],
                                                 product_category=product['product_category'],
                                                 product_description=product['product_description'], unit=product['unit'],
                                                 quantity=product['quantity'])
            product_ids.append(product_id)
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
        ActivityLogs("").add_activity(activity="Create RFQ", done_by=data['_id'], operation_id=requisition_id, operation_type="rfq", type_of_user="buyer")

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
        requisitions = []
        # Get all requisitions for the buyer

        # Loop through add the products and number of responses received for each requisition

        return response.customResponse({"requisitions": requisitions})

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
            prod['documents'] = Document().get_docs(operation_id=prod['product_id'], operation_type="product")
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

# POST request for fetching list of suppliers for buyer
@app.route("/buyer/suppliers/get", methods=["POST"])
@validate_buyer_access_token
def buyer_suppliers_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        buyer_id = BUser(data['_id']).get_buyer_id()
        suppliers = Join().get_suppliers_for_buyers(buyer_id=buyer_id)
        return response.customResponse({"suppliers": suppliers})

    except Exception as e:
        log = Logger(module_name="/buyer/suppliers/get", function_name="buyer_suppliers_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for managing supplier abilities in RFQ
@app.route("/buyer/rfq/suppliers/ops", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_supplier_ops():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        if data['operation_type'] == "unlock":
            if InviteSupplier().update_unlock_status(supplier_id=data['supplier_id'], operation_id=data['requisition_id'], operation_type="rfq", status=data['status']):
                suppliers = Join().get_suppliers_quoting(operation_id=data['requisition_id'], operation_type="rfq")
                return response.customResponse({"response": "Supplier unlocked successfully", "suppliers": suppliers})
            return response.errorResponse("Oops, some error occured. Please try again after sometime")

        if data['operation_type'] == "remove":
            if InviteSupplier().remove_supplier(supplier_id=data['supplier_id'], operation_id=data['requisition_id'], operation_type="rfq"):
                suppliers = Join().get_suppliers_quoting(operation_id=data['requisition_id'], operation_type="rfq")
                return response.customResponse({"response": "Supplier removed from the RFQ successfully", "suppliers": suppliers})
            return response.errorResponse("Oops, some error occured. Please try again after sometime")

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/suppliers/ops", function_name="buyer_rfq_suppliers_ops()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for fetching list of suppliers for buyer
@app.route("/buyer/products/get", methods=["POST"])
@validate_buyer_access_token
def buyer_products_get():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        products = Product().get_buyer_products(buyer_id=data['buyer_id'])
        return response.customResponse({"products": products})

    except Exception as e:
        log = Logger(module_name="/buyer/products/get", function_name="buyer_products_get()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

# POST request for cancelling a RFQ
@app.route("/buyer/rfq/cancel", methods=["POST"])
@validate_buyer_access_token
def buyer_rfq_cancel():
    try:
        data = DictionaryOps.set_primary_key(request.json, "email")
        data['_id'] = data['_id'].lower()
        if Requisition(data['requisition_id']).cancel_rfq():
            return response.customResponse({"response": "RFQ: " + str(data['requisition_id']) + " has been cancelled successfully"})
        return response.errorResponse("Oops, some error occured. Please try again after sometime")

    except Exception as e:
        log = Logger(module_name="/buyer/rfq/cancel", function_name="buyer_rfq_cancel()")
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

        if requisition.get_cancelled():
            return response.errorResponse("You cannot quote against a cancelled RFQ")

        # Checking the unlock status
        if not unlock_status:
            return response.errorResponse("You cannot quote more than once until buyer unlocks you to quote from his dashboard")

        # If supplier is quoting for a closed RFQ
        if GenericOps.get_current_timestamp() > requisition.get_deadline():
            return response.errorResponse("This RFQ is not accepting any further quotations from suppliers")



        # Add quotation
        quotation_id = Quotation().add_quotation(supplier_id=suser.get_supplier_id(), requisition_id=data['requisition_id'],
                                                 remarks=quotation['remarks'], quote_validity=quotation['quote_validity'],
                                                 delivery_time=quotation['delivery_time'], total_amount=quotation['total_amount'],
                                                 total_gst=quotation['total_gst'])
        # Add quotes
        quotes = []
        for quote in quotation['quotes']:
            qt = [quotation_id, quote['charge_id'], quote['charge_name'], quote['quantity'], quote['gst'],
                  quote['per_unit'], quote['amount']]
            qt = tuple(qt)
            quotes.append(qt)
        quotes_id = Quote().insert_many(quotes)

        # Update the unlock_status of supplier
        InviteSupplier().update_unlock_status(supplier_id=supplier_id, operation_id=data['requisition_id'], operation_type="rfq", status=False)

        # Sending a mail to buyer
        supplier_company_name = supplier.get_company_name()
        buyers = Join().get_buyers_for_rfq(data['requisition_id'])
        subject = conf.email_endpoints['supplier']['quotation_submitted']['subject'].replace("{{supplier_company_name}}", supplier_company_name).replace("{{requisition_id}}", str(data['requisition_id']))
        for buyer in buyers:
            p = Process(target=EmailNotifications.send_template_mail, kwargs={"recipients": [buyer['email']],
                                                                              "template": conf.email_endpoints['supplier']['quotation_submitted']['template_id'],
                                                                              "subject": subject,
                                                                              "USER": buyer['name'],
                                                                              "SUPPLIER_NAME": supplier_company_name,
                                                                              "TYPE_OF_REQUEST": "RFQ",
                                                                              "REQUEST_ID": str(data['requisition_id']),
                                                                              "LOT_NAME": buyer['requisition_name']})
            p.start()

        return response.customResponse({"response": "Quotation sent successfully"})

    except Exception as e:
        log = Logger(module_name="/supplier/quotation/send", function_name="supplier_quotation_send()")
        log.log(traceback.format_exc())
        return response.errorResponse("Some error occurred please try again!")

########################################### CONTACT SECTION #####################################################

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, threaded=True)
