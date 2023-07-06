""" implement key/value store """
import pickle
import dill
import dill.detect
import redis
from satosa.state import _AESCipher

import sys
sys.path.append('../venv/lib64/python3.9/site-packages/cryptography')


class LocalStore():
    """ Store context objects in Redis.
        Create a new key when a new value is set.
        Delete key/value delayed after reading it
    """
    def __init__(self, encryption_key: str, redishost: str):
        self.redis = redis.Redis(host=redishost, port=6379)
        self.aes_cipher = _AESCipher(encryption_key)

    def set(self, context: object) -> int:
        context_dilld = dill.dumps(context)
        context_enc = self.aes_cipher.encrypt(context_dilld)
        key = self.redis.incr('REDIRURL_sequence', 1)
        self.redis.set(key, context_enc, 1800)  # generous 30 min timeout to complete SSO transaction
        return key

    def get(self, key: int) -> object:
        context_serlzd = self.redis.get(key)
        self.redis.expire(key, 1800)  # delay deletion: will be needed by subsequent request
        context_dec = self.aes_cipher.decrypt(context_serlzd)
        return pickle.loads(context_dec)
