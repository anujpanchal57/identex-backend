import csv
from utility import DBConnectivity
from pprint import pprint

filename = "pincode_details.csv"

# initializing the titles and rows list
fields = []
rows = []

sql_conn = DBConnectivity.create_sql_connection()
cursor = sql_conn.cursor(dictionary=True)

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting each data row one by one
    for row in csvreader:
        single_row = tuple([row[1], row[4], row[5], row[6], row[7], row[8], row[9]])
        rows.append(single_row)

    # Inserting values in the db
    cursor.executemany("""INSERT INTO pincodes (pincode, division_name, region_name, circle_name, taluka, 
            district_name, state_name) VALUES (%s, %s, %s, %s, %s, %s, %s)""", rows)

    cursor.close()
    sql_conn.close()
