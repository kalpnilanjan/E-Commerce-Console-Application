from cryptography.fernet import Fernet

# Code to generate and store random key for password encryption and decryption
# REFERENCE: https://nitratine.net/blog/post/encryption-and-decryption-in-python/

if __name__=="__main__":
    key = Fernet.generate_key()
    #store the key in file to read and use later
    crpyt_file = open('encrption_key.key', 'wb')
    crpyt_file.write(key)
    crpyt_file.close()

