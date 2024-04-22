import hashlib


class Passgen:
    _secret: str
    _max_length: int

    def __init__(self, secret: str, max_length: int = 256):
        self._secret = secret
        self._max_length = max_length

    def hash(self, password: str) -> str:
        hashable = (self._secret + password).encode()
        return hashlib.sha256(hashable).hexdigest()[: self._max_length]
