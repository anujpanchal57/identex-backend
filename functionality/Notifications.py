import base64
import traceback
import uuid
import os
from pprint import pprint
from database.BuyerOps import Buyer
from database.SupplierOps import Supplier
from database.BuyerUserOps import BUser
from weasyprint import HTML
from database.SupplierUserOps import SUser
from functionality import GenericOps, OSOps, EmailNotifications, response
from functionality.Logger import Logger
from utility import conf
from Integrations.AWSOps import AWS
from database.PurchaseOrderOps import PO

class Notification:
    def __init__(self, checkpoint, file=''):
        self.__checkpoint = checkpoint
        self.__file = file

    def send_notification(self, **kwargs):
        try:
            if self.__checkpoint.lower() == "order_created":
                with open(self.__file, 'r', encoding="utf-8") as order:
                    content = order.read()

                params = {}
                array_params = {}
                details = kwargs['details']
                po_no = details['po_no'].split('/')[0]
                buyer, supplier = Buyer(details['buyer_details']['buyer_id']), Supplier(details['supplier_details']['supplier_id'])
                buyer_details, supplier_details, delivery_details = details['buyer_details'], details['supplier_details'], details['delivery_address']

                # Buyer field details
                params['BUYER_COMPANY'] = buyer_details['company_name']
                params['BUYER_GST_NUMBER'] = buyer_details['gst_no']
                params['BUYER_COMPANY_ADDRESS'], params['BUYER_PIN_CODE'], params['BUYER_COUNTRY'] = buyer_details['business_address'], buyer_details['pincode'], buyer_details['country']
                params['LOGO'] = "https://uploads-idntx.s3.ap-south-1.amazonaws.com/B1002/download+(1).png"
                params['PO_NUMBER'] = details['po_no']
                params['ORDER_DATE'] = details['order_date']

                # Supplier field details
                params['SUPPLIER_COMPANY'] = supplier_details['company_name']
                params['SUPPLIER_GST_NUMBER'] = supplier_details['gst_no']
                params['SUPPLIER_BUSINESS_ADDRESS'] = supplier_details['business_address']
                params['SUPPLIER_PIN_CODE'] = supplier_details['pincode']
                params['SUPPLIER_COUNTRY'] = supplier_details['country']

                # Delivery fields
                params['BUYER_DELIVERY_ADDRESS'] = delivery_details['company_address']
                params['BUYER_DELIVERY_PIN_CODE'], params['BUYER_DELIVERY_COUNTRY'] = delivery_details['pincode'], delivery_details['country']

                # Payment terms and other fields
                params['CREDIT_TERMS'], params['FREIGHT_INCLUDED'] = details['payment_terms'], details['freight_included']
                params['TERMS_CONDITIONS'], params['PREPARED_BY'], params['APPROVED_BY'] = details['tnc'], BUser(details['prepared_by']).get_name(), BUser(details['approved_by']).get_name()

                # Products list and totals fields
                array_params['PRODUCTS_INFO'] = GenericOps.populate_product_line_items(details['line_items'], details['unit_currency'])
                sub_total, total_gst = GenericOps.round_of(details['total_amount']), GenericOps.round_of(details['total_gst'])
                grand_total = GenericOps.round_of(sub_total + total_gst)
                params['SUB_TOTAL'] = details['unit_currency'].upper() + " " + str(sub_total)
                params['TOTAL_GST'] = details['unit_currency'].upper() + " " + str(total_gst)
                params['GRAND_TOTAL'] = details['unit_currency'].upper() + " " + str(grand_total)
                for key, val in params.items():
                    content = content.replace("{{" + str(key) +  "}}", str(val))

                for key, val in array_params.items():
                    content = content.replace("{{{" + str(key) + "}}}", str(val))

                if not OSOps.path_exists(conf.upload_documentation):
                    OSOps.create_directory(conf.upload_documentation)
                temp_file_path = conf.upload_documentation + str(uuid.uuid4()) + ".html"
                temp_file = open(temp_file_path, 'w', encoding='utf-8')
                temp_file.write(content)
                complete_path = conf.upload_documentation
                if not OSOps.path_exists(complete_path):
                    OSOps.create_directory(complete_path)
                HTML(temp_file_path).write_pdf(complete_path + po_no + "_order_created.pdf")
                ## UNCOMMENT THIS LINE BEFORE PUSHING
                OSOps.deletefile(temp_file_path)
                pdf_path = complete_path + po_no + "_order_created.pdf"
                aws_file_name = po_no + "_order_created"
                data = open(pdf_path, 'rb').read()
                base64_encoded = base64.b64encode(data).decode('UTF-8')
                upload_file_path = GenericOps.generate_aws_file_path(client_type="buyer", client_id=buyer_details['buyer_id'],
                                                                     document_type="pdf", notification_type='order_upload',
                                                                     file_name=aws_file_name)
                file_link = AWS('s3').upload_file_from_base64(base64_string=base64_encoded, path=upload_file_path)
                # Updating po_url in purchase_orders table
                PO(details['po_id']).update_po_url(file_link)
                suser = SUser(supplier_id=supplier_details['supplier_id'])
                po_no_display = "inline" if details['po_no'] != "" else "none"
                op_display = "inline" if details['acquisition_id'] != 0 and details['acquisition_type'].lower() != "adhoc" else "none"
                products = []
                for lt in details['line_items']:
                    products.append({"delivery_date": GenericOps.convert_timestamp_to_datestr(lt['delivery_date']),
                                     "product_name": lt['product_name'],
                                     "product_description": lt['product_description'],
                                     "amount": str(lt['amount'])})

                subject = conf.email_endpoints['buyer'][self.__checkpoint]['subject'].replace("{{po_number}}",details['po_no']).replace("{{buyer_company_name}}", buyer.get_company_name())
                link = conf.SUPPLIERS_ENDPOINT + conf.email_endpoints['buyer']['order_created']['page_url']
                documents = [{"document_name": aws_file_name + ".pdf", "document_url": file_link}]
                EmailNotifications.send_handlebars_email(
                    template=conf.email_endpoints['buyer'][self.__checkpoint]['template_id'],
                    subject=subject,
                    recipients=[suser.get_email()],
                    USER=suser.get_first_name(),
                    BUYER_COMPANY_NAME=buyer.get_company_name(),
                    PO_NUMBER_DISPLAY=po_no_display,
                    OPERATION_DISPLAY=op_display,
                    PO_NUMBER=details['po_no'],
                    OPERATION=details['acquisition_type'].upper(),
                    OPERATION_ID=str(details['acquisition_id']),
                    LOT_NAME=details['lot_name'],
                    LINK=link,
                    PRODUCTS=products,
                    documents=documents
                )
            return True

        except Exception as e:
            log = Logger(module_name="Notifications", function_name="send_notification()")
            log.log(traceback.format_exc())
            return response.errorResponse("Some error occurred please try again!")