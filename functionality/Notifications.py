from pprint import pprint
from database.BuyerOps import Buyer
from database.SupplierOps import Supplier
from database.BuyerUserOps import BUser
from bs4 import BeautifulSoup
from functionality import GenericOps

class Notification:
    def __init__(self, checkpoint, file=''):
        self.__checkpoint = checkpoint
        self.__file = file

    def send_notification(self, **kwargs):
        if self.__checkpoint.lower() == "order_created":
            with open(self.__file, 'r',encoding="utf-8") as booking:
                content = booking.read()
                soup = BeautifulSoup(content)

            params = {}
            array_params = {}
            details = kwargs['details']
            buyer, supplier = Buyer(details['buyer_details']['buyer_id']), Supplier(details['supplier_details']['supplier_id'])
            buyer_details, supplier_details, delivery_details = details['buyer_details'], details['supplier_details'], details['delivery_address']

            # Buyer field details
            params['BUYER_COMPANY'] = buyer_details['company_name'],
            params['BUYER_GST_NUMBER'] = buyer_details['gst_no']
            params['BUYER_COMPANY_ADDRESS'], params['BUYER_PIN_CODE'], params['BUYER_COUNTRY'] = buyer_details['business_address'], buyer_details['pincode'], buyer_details['country']
            params['LOGO'] = buyer.get_company_logo()
            params['PO_NUMBER'] = details['po_no']
            params['ORDER_DATE'] = details['order_date']

            # Supplier field details
            params['SUPPLIER_COMPANY'] = supplier_details['company_name']
            params['SUPPLIER_GST_NUMBER'] = supplier_details['gst_no']
            params['SUPPLIER_BUSINESS_ADDRESS'] = supplier_details['gst_no']
            params['SUPPLIER_PIN_CODE'] = supplier_details['pincode']
            params['SUPPLIER_COUNTRY'] = supplier_details['country']

            # Delivery fields
            params['BUYER_DELIVERY_ADDRESS'] = delivery_details['company_address']
            params['BUYER_DELIVERY_PIN_CODE'], params['BUYER_DELIVERY_COUNTRY'] = delivery_details['pincode'], delivery_details['country']

            params['CREDIT_TERMS'], params['FREIGHT_INCLUDED'] = details['payment_terms'], details['FREIGHT_INCLUDED']
            params['TERMS_CONDITIONS'], params['PREPARED_BY'], params['APPROVED_BY'] = details['tnc'], BUser(details['prepared_by']).get_name(), BUser(details['approved_by']).get_name()


        return True

# details = {
#     "po_no": "1000/20-21/Bhavani",
#     "unit_currency": "inr",
#     "order_date": "20-10-2020",
#     "acquisition_id": 1000,
#     "acquisition_type": "rfq",
#     "buyer_details": {
#         "buyer_id": 1000,
#         "company_name": "Bhavani Fabricators",
#         "gst_no": "27AKFPP0597A1Z8",
#         "business_address": "Wagle Estate",
#         "city": "",
#         "pincode": "400610",
#         "country": "India"
#     },
#     "supplier_details": {
#         "supplier_id": 1000,
#         "company_name": "ABC pvt ltd",
#         "gst_no": "27AKFPP0597A1Z8",
#         "business_address": "Wagle Estate",
#         "city": "",
#         "pincode": "400610",
#         "country": "India"
#     },
#     "delivery_address": {
#         "company_name": "ABC pvt ltd",
#         "company_address": "Wagle Estate",
#         "pincode": "400610",
#         "country": "India"
#     },
#     "line_items": [{
#         "quote_id": 1001,
#         "product_id": 1001,
#         "product_name": "copper ball bearings",
#         "product_description": "Should be made of copper",
#         "quantity": 3,
#         "delivery_date": 1603197932,
#         "gst": 18,
#         "per_unit": 14000,
#         "unit": "nos",
#         "amount": 20000
#     }],
#     "total_amount": 20000,
#     "total_gst": 14000,
#     "tnc": "sample tnc",
#     "payment_terms": "abc",
#     "freight_included": "yes/no",
#     "prepared_by": "anuj.panchal@exportify.in",
#     "approved_by": "anuj.panchal@exportify.in"
# }

# pprint(Notification("order_created").send_notification(details=details))