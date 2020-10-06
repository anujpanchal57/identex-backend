from cerberus import Validator
# class CerberusValidator(Validator):
#     def _validate_name(self, field, value):
#         if


class IncompleteKycForm(Exception):
    pass


class InvalidSearchQueryException(Exception):
    pass


class RequestTimedOut(Exception):
    pass


class InvalidBankAccountDetails(Exception):
    pass

class IncompleteRequestException(Exception):
    def __init__(self, error):
        self.error = error

class BadRequestException(Exception):
    def __init__(self, error):
        self.error = error

class InvalidLoginCredentials(Exception):
    def __init__(self, error):
        self.error = error

class AccountVerified(Exception):
    pass

class UserNotFound(Exception):
    pass

class AgentNotFound(Exception):
     def __init__(self, error):
         self.error = error

class EmailNotFound(Exception):
    pass