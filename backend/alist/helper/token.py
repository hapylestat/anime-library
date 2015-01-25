
import os
import hashlib
import hmac
import time
from binascii import hexlify
import json
import base64

_DEFAULT_TIMEOUT = 5 * 60
_DEFAULT_HASHMOD = "sha256"


class TokenHelper(object):
  def __init__(self, secret=None, token_life=_DEFAULT_TIMEOUT):
    self._hash_name = _DEFAULT_HASHMOD
    self._hash = getattr(hashlib, _DEFAULT_HASHMOD)
    self._hash_size = self._hash().digest_size
    if isinstance(secret, str):
      self._secret = bytes(secret, "utf8")
    else:
      self._secret = secret

    self._token_life = token_life
    self._sig_secret = self.create_sig_secret()

  def create_sig_secret(self):
    message = bytes(__file__, "utf8")
    pre_key = hmac.new(b"\x00" * self._hash_size, self._secret, self._hash).digest()
    tmp = b""
    key = []
    for i in [1, 2]:
      cdata = tmp + message + bytes((i,))
      cdata = hmac.new(pre_key, cdata, self._hash).digest()
      key.append(cdata)
    return b"".join(key)[:self._hash_size]

  def _get_signature(self, value):
    return hmac.new(self._sig_secret, value, self._hash).digest()

  def make_token(self, data):
    data = dict(data)
    data["salt"] = hexlify(os.urandom(4)).decode("utf-8")
    data["expires"] = time.time() + self._token_life
    payload = json.dumps(data).encode("utf-8")
    sig = self._get_signature(payload)
    return base64.urlsafe_b64encode(payload + sig).decode("utf-8")

  def parse_token(self, token):
    token = base64.urlsafe_b64decode(token)
    sig = token[-self._hash_size:]
    payload = token[:-self._hash_size]

    expected_sig = self._get_signature(payload)

    if not hmac.compare_digest(sig, expected_sig):
      raise Exception("Signature error")

    data = json.loads(payload.decode("utf-8"))
    if data["expires"] <= time.time():
      raise Exception("Tocken expired")

    return data


