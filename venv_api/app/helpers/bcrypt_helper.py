import bcrypt

def hash_password(password: str):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_pwd = bcrypt.hashpw(bytes, salt)
    encode_pwd = hash_pwd.decode()

    return encode_pwd