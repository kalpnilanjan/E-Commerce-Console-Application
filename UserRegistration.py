from pymongo import MongoClient
from pprint import pprint
import getpass
from cryptography.fernet import Fernet
import re

# REFERENCE: https://nitratine.net/blog/post/encryption-and-decryption-in-python/
# REFERENCE: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/

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

def update_users(users, filter, updates):
    result = users.update_one(filter, updates)
    return result.modified_count

# Main Function
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
    users = db.users
    print('WELCOME TO THE USER REGISTRATION PAGE!!')

    while True:
        ch = int(input('\n1. Create Account\t2. Update Account\t3. Delete Account\t4.Exit\nEnter a choice: '))
        # Create new account
        if (ch == 1):
            name = input('Enter the name of the user: ')
            email_id = input('Enter email id: ')
            # Validate Email-Id
            while True:
                if(re.search(regex, email_id)):
                    while True:
                        query = {'emailId': email_id}
                        if (users.count_documents({'emailId': email_id}) > 0):
                            email_id = input('Email-Id already exists. Enter new email id: ')
                        else:
                            break
                    break
                else:
                    email_id = input('Invalid email id. Enter a new email id: ')
            password = getpass.getpass(prompt='Enter Password: ')
            encrypted_password = fernet_key.encrypt(password.encode())
            address = input('Enter address: ')
            phone = input('Enter phone number: ')
            data = {'name' : name, 'emailId' : email_id, 'password' : encrypted_password,
                    'address' : [address], 'phone' : [phone]}
            user_id = users.insert_one(data)
            print('User added to the database with id: ', user_id)

        # Update existing account
        elif (ch == 2):
            auth_email = input('Enter email id: ')
            auth_pwd = getpass.getpass(prompt='Enter password: ')
            valid, auth_email = auth_user(auth_email, auth_pwd, users, fernet_key)
            if valid:
                filter = {'emailId' : auth_email}
                while True:
                    upd_ch = int(input('\n1. Update name\t2. Add new phone\t3. Add new address\t4. Exit\nEnter your choice: '))
                    if (upd_ch == 1):
                        new_name = input('Enter new name: ')
                        name_upd = update_users(users, filter, {'$set' :  {'name' : new_name}})
                        print(name_upd,' users updated.')
                    elif (upd_ch == 2):
                        new_phone = input('Enter new phone: ')
                        phone_upd = update_users(users, filter, {'$push': {'phone': new_phone}})
                        print(phone_upd, ' users updated.')
                    elif (upd_ch == 3):
                        new_address = input('Enter new address: ')
                        add_upd = update_users(users, filter, {'$push': {'address': new_address}})
                        print(add_upd, ' users updated.')
                    else:
                        break
            else:
                print('User not found')
                break

        # Delete account
        elif (ch == 3):
            del_email = input('Enter email id: ')
            del_pwd = getpass.getpass(prompt='Enter password: ')
            valid, del_email = auth_user(del_email, del_pwd, users, fernet_key)
            if valid:
                query = {'emailId' : del_email}
                x = users.delete_many(query)
                print(x.deleted_count, " user deleted")
            else:
                print('User not found')
                break

        # Exit
        else:
            print('Exiting')
            break
