from pymongo import MongoClient
from pprint import pprint
import getpass
import json
from cryptography.fernet import Fernet
import re
import pandas as pd

#REFERENCES: https://stackoverflow.com/questions/20727257/query-on-top-n-rows-in-mongodb

regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

def auth_user(auth_email, auth_pwd, users, fernet_key):
    count = 0
    while count != 4:
        count += 1
        query = {'emailId': auth_email}
        if re.search(regex, auth_email) and (users.count_documents(query) > 0):
            cursor = users.find_one(query)
            get_pwd = cursor['password']
            if (auth_pwd.encode() == fernet_key.decrypt(get_pwd)):
                print('Login Successful!!')
                return True, auth_email
        elif count == 4:
            return False, auth_email
        elif not re.search(regex, auth_email):
            auth_email = input('Invalid email-id. Enter valid email: ')
        else:
            auth_email = input('No records found for given email. Enter new email id: ')
    return False, auth_email


def print_table(cursor, cols):
    # Insert data from cursor into array
    #items = [data for data in cursor]
    items = list(cursor)
    # convert array to pandas dataframe
    items_df = pd.DataFrame(items)
    # Print all the titles
    low = 0
    high = 9
    len = items_df.shape[0]
    print('Total documents fetched: ', len)
    while True:
        if cols == None:
            print(items_df.loc[low:high, :])
        else:
            print(items_df.loc[low:high, cols])
        low = high + 1
        high = high + 10
        if len > low:
            view = input('Print more? Y/N: ')
            if view.upper() != 'Y':
                break
        else:
            break

# Main Function
if __name__=="__main__":
    # Read encryption key from file
    file = open('encrption_key.key', 'rb')
    encryption_key = file.read()
    fernet_key = Fernet(encryption_key)
    file.close()

    # Connect to MongoDB
    client = MongoClient("mongodb://<server>/<dbname>")
    # database
    db = client.testDB
    # users collection
    users = db.users
    # items collection
    items = db.coll

    print('WELCOME TO THE USER OPERATIONS PAGE!!')
    email = input('\nEnter email-id: ')
    password = getpass.getpass(prompt='Enter Password: ')
    is_valid, email = auth_user(email, password, users, fernet_key)

    while is_valid:
        choice = int(input('\n1. Find items by  main category\t\t2. Find items is present in sub category'
                           '\t3. Find items in price range\n4. Find products by brand\t\t5. Find items by name'
                           '\t\t\t\t6. Find books by rank\n7. Find all brands in category\t\t8. Exit\nEnter your choice: '))
        if (choice == 1):
            main_cat = input('Enter the name of the category: ')
            main_cat_data = items.find({'main_cat' : main_cat.capitalize()})
            print_table(main_cat_data, ['title', 'brand', 'price'])

        elif (choice == 2):
            category = input('Enter the category to fetch items from: ')
            sub_cat_data = items.find({'category' : {'$in' : [category.capitalize()]}})
            print_table(sub_cat_data, ['title', 'brand', 'price'])

        elif (choice == 3):
            min_range, max_range = [int(x) for x in input("Enter the minimum and maximum value: ").split()]
            cat = input('Enter the category (null - no category): ')
            if(cat.lower() == 'null'):
                range_data = items.find({'price' : {'$gte' : min_range, '$lte': max_range}})
            else:
                range_data = items.find({'$and': [{'price': {'$gte': min_range, '$lte': max_range}}, {'main_cat' : cat.capitalize()}]})
            print_table(range_data, ['title', 'price'])

        elif (choice == 4):
            brand = input('Enter the brand to fetch items from: ')
            regex_brand = '.*' + brand + '.*'
            brand_data = items.find({'brand': {'$regex': regex_brand, '$options':'i'}})
            print_table(brand_data, ['title', 'price', 'main_cat'])

        elif (choice == 5):
            name_val = input('Enter the name of the item: ')
            regex = '.*' + name_val + '.*'
            title_data = items.find({"title": {"$regex": regex, "$options": 'i'}})
            print_table(title_data, ['title', 'price', 'main_cat'])

        elif (choice == 6):
            num = int(input('Enter the number of books to be fetched: '))
            pipeline = [{'$match':{'main_cat': 'Books'}}, {'$sort': {'rank' : 1}}, {'$limit': num}]
            books_data = items.aggregate(pipeline)
            print_table(books_data, ['title', 'price'])

        elif (choice == 7):
            category = input('Enter the category: ')
            brands_cat = items.find({'main_cat': category.capitalize()}).distinct('brand')
            print_table(brands_cat, None)

        else:
            if(choice != 8):
                print('Invalid choice. Exiting the page.')
            break
