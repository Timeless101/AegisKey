import pytest
from cryptography.fernet import Fernet

import src.crypto as crypto
import src.common.errors as errors


def test_password_decryption_with_wrong_key_raises_decryption_error():
    correct_key = Fernet.generate_key()
    wrong_key = Fernet.generate_key()
    encrypted_password = Fernet(correct_key).encrypt(b"secret")

    with pytest.raises(errors.DecryptionError):
        crypto.password_decryption(
            encryption_key=wrong_key,
            password=encrypted_password
        )


def test_password_decryption_with_corrupt_ciphertext_raises_decryption_error():
    key = Fernet.generate_key()

    with pytest.raises(errors.DecryptionError):
        crypto.password_decryption(
            encryption_key=key,
            password=b"not-valid-fernet-data"
        )
