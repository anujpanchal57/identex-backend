from utility import DBConnectivity, conf
from pprint import pprint

sql_conn = DBConnectivity.create_sql_connection()
cursor = sql_conn.cursor(dictionary=True)

# fetch all the orders
cursor.execute("""select * from orders""")
orders = cursor.fetchall()

if len(orders) > 0:
    for i in range(len(orders)):
        # Fetch quote
        cursor.execute("""select * from quotes where quote_id = %s""", (orders[i]['quote_id'], ))
        quote = cursor.fetchone()
        cursor.execute("""select product_id, product_description from products 
                            where reqn_product_id = %s""", (orders[i]['reqn_product_id'], ))
        product = cursor.fetchone()
        print(product)
        # Insert quote details in the order table
        if len(quote) > 0:
            cursor.execute("update orders set quantity = " + str(quote['quantity']) + ", gst = " + str(quote['gst']) + ", per_unit = " + str(quote['per_unit']) + ", amount = " + str(quote['amount']) + ", delivery_time = " + str(quote['delivery_time']) + ", product_description = '" + str(product['product_description']) + "', reqn_product_id = " + str(product['product_id']) + " where order_id = " + str(orders[i]['order_id']))
