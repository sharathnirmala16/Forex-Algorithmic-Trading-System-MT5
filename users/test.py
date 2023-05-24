import temp_crypto

message = 'Hello'
password = '12345'

cipher = temp_crypto.encrypt(message, password)
print(cipher)
plaintext = temp_crypto.decrypt(cipher, password)
print(plaintext)