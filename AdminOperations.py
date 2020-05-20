from pymongo import MongoClient
from pprint import pprint
import getpass
import pandas as pd
from bson.objectid import ObjectId
from cryptography.fernet import Fernet
import json
import bson

#REFERENCE: https://stackoverflow.com/questions/17805304/how-can-i-load-data-from-mongodb-collection-into-pandas-dataframe

# Fucntion to print title from the documents
def print_title(items):
    print('\nPrinting titles of documents.')
    # Insert data from cursor into array
    inventory_data = [data for data in items]
    # convert array to pandas dataframe
    df_inventory_data = pd.DataFrame(inventory_data)
    # Print all the titles
    print(df_inventory_data['title'])

def print_table(cursor):
    print('\nPrinting fetched documents.')
    # Insert data from cursor into array
    #items = [data for data in cursor]
    items = list(cursor.find())
    # convert array to pandas dataframe
    items_df = pd.DataFrame(items)
    print(items_df)

def auth_user(user_name, auth_pwd, admin_table, fernet_key):
    count = 0
    while count != 4:
        count += 1
        query = {'username': user_name}
        if (admin_table.count_documents(query) > 0):
            cursor = admin_table.find_one(query)
            get_pwd = cursor['password']
            if (auth_pwd.encode() == fernet_key.decrypt(get_pwd)):
                print('Login Successful!!')
                return True, user_name
        elif count == 4:
            return False, user_name
        else:
            user_name = input('No records found for given username. Enter new admin username: ')
    return False, user_name

# Function to insert new items into the table
def insert_function(items_collection):
    str = input("Enter the document that needs to be inserted: ")
    #Convert input to json string
    data = json.loads(str)
    #insert into mongodb and print the _id
    ins = items_collection.insert(data)
    print("Product inserted successfully with id: ", ins)
    after_insert = items_collection.find({'_id': ObjectId(ins)})
    for doc in after_insert:
        pprint(doc)

# Function to update value of existing documents
def update_function(items_collection):
    str = input("Enter the title of the item to be updated: ")
    query = {"title": str}
    updated_str = input('Enter the json string that needs to be updated: ')
    update_val = json.loads(updated_str)
    result = items_collection.update_one(query, {'$set' : update_val})
    print(result.modified_count, "document updated")
    after_update = items_collection.find(query)
    for doc in after_update:
        pprint(doc)


# Delete function to delete an item using title
def delete_function(items_collection):
    str = input("Enter the title of the item to be deleted: ")
    regex = '.*' + str + '.*'
    items = items_collection.find({"title": {"$regex": regex, "$options": 'i'}})
    print_title(items)
    num = input("Enter the item number to be deleted (0-indexed): ")
    num = int(num)
    pos = 0
    for itr in items.rewind():
        print(pos, 'num:', num)
        if pos == num:
            print(itr['_id'])
            items_collection.delete_one({"_id": ObjectId(itr['_id'])})
            print('Document deleted.')
            break
        else:
            pos += 1
    items = items_collection.find({"title": {"$regex": regex, "$options": 'i'}})
    print('\nAfter deleting the item')
    print_title(items)

# Main Function
if __name__=="__main__":

    file = open('encrption_key.key', 'rb')
    encryption_key = file.read()
    fernet_key = Fernet(encryption_key)
    file.close()

    client = MongoClient("mongodb://<server>/<dbname>")
    #database
    db = client.testDB
    #collection name
    items_collection = db.coll

    print("WELCOME TO THE ADMIN INVENTORY SECTION!!")
    # Add, update, delete product
    admin_name = input('\nEnter username: ')
    password = getpass.getpass(prompt='Enter Password: ')
    is_valid, username = auth_user(admin_name, password, db.admin_table, fernet_key)
    if is_valid:
        while True:
            choice = int(input("\n1. Insert new item\t2. Delete an item\t3. Update an item\n4. Check Inventory\t5. Exit\nSelect an operation: "))
            if(choice == 1):
                insert_function(items_collection)
            elif (choice == 2):
                delete_function(items_collection)
            elif (choice == 3):
                update_function(items_collection)
            elif (choice == 4):
                ch = int(input('\n1. Number of items per brand\t2. Number of items per category\t3.Exit\nEnter your choice:'))
                if (ch == 1):
                    cat = input('Enter the category: ')
                    regex_brand = '.*' + cat + '.*'
                    map = bson.Code("""function(){
                    emit(this.brand,1);
                    }""")
                    reduce = bson.Code("function (key, values) {"
                                  "  var total = 0;"
                                  "  for (var i = 0; i < values.length; i++) {"
                                  "    total += values[i];"
                                  "  }"
                                  "  return total;"
                                  "}")
                    #query_main
                    val = items_collection.map_reduce(map, reduce, out = 'output', query = {'main_cat' : {'$regex': regex_brand, '$options':'i'}})
                    print_table(val)
                elif (ch == 2):
                    map = bson.Code("""function(){
                                        emit(this.main_cat, 1);
                                        }""")

                    reduce = bson.Code("function (key, values) {"
                                       "  var total = 0;"
                                       "  for (var i = 0; i < values.length; i++) {"
                                       "    total += values[i];"
                                       "  }"
                                       "  return total;"
                                       "}")
                    val = items_collection.map_reduce(map, reduce, 'output')
                    print_table(val)
                else:
                    break
            else:
                break
    else:
        print('Invalid password')


