from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.fernet import Fernet, InvalidToken
import base64
import cryptography
import os
import src.common.errors as errors

def password_decryption(encryption_key: bytes, password: bytes) -> str:
    try:
        f: Fernet = Fernet(encryption_key)
        decrypted_password: bytes = f.decrypt(password)
        return decrypted_password.decode("utf-8")
    except (InvalidToken, ValueError, UnicodeDecodeError) as decrypt_error:
        raise errors.DecryptionError("Password could not be decrypted.") from decrypt_error

def password_encryption(encryption_key: bytes, password: str) -> bytes:
    f: Fernet = Fernet(encryption_key)
    return f.encrypt(password.encode("utf-8"))

#Hash password, create key for encryption.
def hash_password(password: str) -> tuple[bytes, bytes, bytes]:

    salt_masterpassword: bytes = os.urandom(16)
    salt_encryption: bytes = os.urandom(16)
    password: bytes = password.encode("utf-8")

    kdf_masterpassword: bytes = Argon2id(
            salt=salt_masterpassword,
            length=64,
            iterations=2,
            lanes=4,
            memory_cost=512*1024, #512 MiB RAM
            ad=None,
            secret=None
    )

    return kdf_masterpassword.derive(password), salt_masterpassword, salt_encryption

#Check password to hash.
def verify_password(input_password: str, database_password: bytes, salt: bytes) -> bool:

    kdf: bytes = Argon2id(
                salt=salt,
                length=64,
                iterations=2,
                lanes=4,
                memory_cost=512*1024, #512 MiB RAM
                ad=None,
                secret=None
            )

    try:
        if kdf.verify(input_password.encode("utf-8"), database_password) is None:
            return True

    except cryptography.exceptions.InvalidKey:
        return False


def login_key_calculation(input_password: bytes , encryption_salt: bytes,) -> bytes:
    kdf_encryption: bytes = Argon2id(
            salt=encryption_salt,
            length=32,
            iterations=2,
            lanes=4,
            memory_cost=512*1024,
            ad=None,
            secret=None
        )

    return base64.urlsafe_b64encode(kdf_encryption.derive(input_password.encode("utf-8")))

if __name__ == "__main__":
    ...
