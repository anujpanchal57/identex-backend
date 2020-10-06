import os
import sys

app_name = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])

sys.path.append(app_name)

from utility import DBConnectivity

import csv

result = []
sql = DBConnectivity.create_sql_connection()
cursor = sql.cursor(dictionary=True)

with open('India_mart_categories_master (1).csv', 'rt')as f:
    data = csv.reader(f)
    counter = 0
    sample = {}
    mapper={}
    categories = {}
    sub_categories = {}
    products = {}
    completed={'categories':[], 'sub_categories': [], 'products': []}
    for row in data:
        row_counter = 0
        for elem in row:
            if counter == 0:
                sample[elem] = ''
                mapper[row_counter] = elem
            else:
                if row_counter == 0 and elem not in categories:
                    cursor.execute("""SELECT `category_id` FROM `idntx_category` WHERE `category_name`= %s""", (elem, ))
                    validate_category = cursor.fetchone()
                    if not validate_category:
                        cursor.execute("""INSERT INTO `idntx_category` (`category_id`, `category_name`) VALUES (NULL, %s)""",(elem, ))
                        cursor.execute("""SELECT `category_id` FROM `idntx_category` WHERE `category_name`= %s""", (elem, ))
                        validate_category = cursor.fetchone()
                    categories[elem] = validate_category['category_id']
                if row_counter == 1 and elem not in sub_categories:
                    cursor.execute("""SELECT `sub_category_id` FROM `idntx_sub_categories` WHERE `sub_category_name`= %s and `category_id` = %s""", (elem, categories[row[0]]))
                    validate_sub_category = cursor.fetchone()
                    if not validate_sub_category:
                        cursor.execute("""INSERT INTO `idntx_sub_categories`(`sub_category_id`, `sub_category_name`, `category_id`) VALUES (NULL,%s,%s)""",(elem, categories[row[0]]))
                        cursor.execute("""SELECT `sub_category_id` FROM `idntx_sub_categories` WHERE `sub_category_name`= %s and `category_id` = %s""", (elem, categories[row[0]]))
                        validate_sub_category = cursor.fetchone()
                    sub_categories[elem] = validate_sub_category['sub_category_id']
                if row_counter == 2 and elem not in products:
                    cursor.execute("""SELECT `product_id` FROM `idntx_products` WHERE `product_name` = %s and `category_id` = %s and `sub_category_id`= %s""", (elem, categories[row[0]], sub_categories[row[1]]))
                    validate_products = cursor.fetchone()
                    if not validate_products:
                        cursor.execute("""INSERT INTO `idntx_products`(`product_id`, `product_name`, `sub_category_id`, `category_id`)
                        VALUES (NULL,%s,%s,%s)""", (elem, sub_categories[row[1]], categories[row[0]]))
                        cursor.execute("""SELECT `product_id` FROM `idntx_products` WHERE `product_name` = %s and `category_id` = %s and `sub_category_id`= %s""", (elem, categories[row[0]], sub_categories[row[1]]))
                        validate_products = cursor.fetchone()
                    print(validate_products)
                    products[elem] = validate_products['product_id']
                sample[mapper[row_counter]] = elem
            row_counter += 1
        if counter >= 1:
            result.append(sample.copy())
        counter += 1
