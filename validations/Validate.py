import re
from pprint import pprint
from cerberus import Validator
from exceptions import exceptions

def validate_signup_auth(req):
    schema = {
        '_id': {'type': 'string', 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', 'required': True,
                'empty': False},
        'name': {'type': 'string', 'regex': '^([A-Za-z]\s*)+$', 'required': True, 'empty': False},
        'mobile': {'type': 'string', 'minlength': 10, 'maxlength': 12, 'required': True, 'empty': False},
        'company_name': {'type': 'string', 'required': True, 'empty': False},
        'password': {'type': 'string', 'required': True, 'empty': False}
    }

    v = Validator(schema)
    if v.validate(req, schema):
        return True
    return exceptions.IncompleteRequestException(v.errors)

def validate_add_agent(req):
    schema = {
        '_id': {'type': 'string', 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', 'required': True,
                'empty': False},
        'name': {'type': 'string', 'regex': '^([A-Za-z]\s*)+$', 'required': True, 'empty': False},
        'mobile': {'type': 'string', 'minlength': 10, 'maxlength': 12, 'required': True, 'empty': False},
        'password': {'type': 'string', 'required': True, 'empty': False},
        'role': {'type': 'list', 'required': True, 'empty': False}
    }

    v = Validator(schema)
    if v.validate(req, schema):
        return True
    # pprint(str(v.errors))
    return exceptions.IncompleteRequestException(v.errors)

def validate_kyc_details(req):
    schema = {
        "_id": {"type": "string", 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', 'required': True, 'empty': False},
        "submit": {"type": "boolean", "required": True, "empty": False},
        "step_no": {"type": "number", "required": True, "empty": False},
        "company_id": {"type": "string", "required": False},
        "profile_details": {
            "type": "dict", "required": True, "empty": False,
            "schema": {
                "full_business_name": {"type": "string", "required": True, "empty": False},
                "company_website": {"type": "string","empty": True},
                "work_phone": {"type": "string", "required": True, "empty": False},
                "iec_no": {"type": "string", "required": True, "empty": False},
                "state": {"type": "string", "required": True, "empty": False},
                "pin_code": {"type": "string", "required": True, "empty": False},
                "organisation_type": {"type": "string", "required": True, "empty": False},
                "pan": {"type": "string", "required": True, "empty": False},
                "principal_business_address": {"type": "string", "required": True, "empty": False},
                "city": {"type": "string", "required": True, "empty": False},
                "documents": {"type": "list", "required": True},
                "declared_by": {"type": "dict", "required": False},
                "submitted_by": {"type": "dict", "required": False}
            }
        }
    }

    v = Validator(schema)
    if v.validate(req):
        return True
    raise exceptions.IncompleteRequestException(v.errors)

def validate_modify_member(req):
    schema = {
        "_id": {"type": "string", 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', 'required': True, 'empty': False},
        "truncate": {"type": "boolean", "required": True, "empty": False},
        "member_details": {
            "type": "dict", "required":False,
            "schema": {
                "name": {"type": "string", "required": True, "empty": False},
                "email": {"type": "string", "required": True, "empty": False},
                "mobile": {"type": "string", "required": False, "empty": True},
                "whatsapp_enabled": {"type": "boolean", "required": True, "empty": False}
            }
        },
        "members": {"type": "list", "required": False}
    }

    v = Validator(schema)
    if v.validate(req):
        return True
    raise exceptions.IncompleteRequestException(v.errors)

# data = {
#         "_id": "anujpanchal57@gmail.com",
#         "company_id": "",
#         "profile_details": {
#             "full_business_name": "ABC",
#             "work_phone": "919952463584",
#             "company_website": "",
#             "iec_no": "1204552368",
#             "state": "Maharashtra",
#             "pin_code": "400120",
#             "organisation_type": "LLP",
#             "pan": "CKF45131581",
#             "principal_business_address": "Marol Naka",
#             "documents": [{
#             "document_name": "custom.jpg",
#             "url": "https://res.cloudinary.com/exportify/image/upload/v1568633857/booking_documents/Exportify/utkarsh.dhawan%40exportify.in/MSDS_1568633856.jpg",
#             "author": "anuj.panchal@exportify.in",
#             "timestamp": 1561638979
#             }, {
#                 "document_name": "advance.jpg",
#                 "url": "https://res.cloudinary.com/exportify/image/upload/v1568633857/booking_documents/Exportify/utkarsh.dhawan%40exportify.in/MSDS_1568633856.jpg",
#                 "author": "anuj.panchal@exportify.in",
#                 "timestamp": 1561638979
#             }]
#         },
#         "submit": True
# }
#
# pprint(validate_kyc_details(data))
