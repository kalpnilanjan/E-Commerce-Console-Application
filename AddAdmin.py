from pymongo import MongoClient
from pprint import pprint
import getpass
from cryptography.fernet import Fernet

# Used to add admins for the inventory management

if __name__=="__main__":
    # Read encryption key from file
    file = open('encrption_key.key', 'rb')
    encryption_key = file.read()
    fernet_key = Fernet(encryption_key)
    file.close()

    #Connect to mongoDB
    client = MongoClient("mongodb://<server>/<dbname>")
    #database
    db = client.testDB
    #collection name
    users = db.admin_table
    print('WELCOME TO THE ADMIN REGISTRATION PAGE')

    admin_name = input('Enter username: ')
    password = getpass.getpass(prompt='Enter Password: ')

    encrypted_password = fernet_key.encrypt(password.encode())
    data = {'username': admin_name, 'password': encrypted_password}
    admin_id = users.insert(data)
    print('User added to the database with id: ', admin_id)