import hmac
import time
import base64
from hashlib import sha256
from urllib.parse import urlencode


SECRET = ("super-secret-change-me").encode()


# Very lightweight signed-URL generator for dev/self-hosting.
# For S3/CloudFront, switch to their native signed URL solutions.


def sign_url(url: str, ttl_seconds: int = 3600) -> str:
exp = int(time.time()) + ttl_seconds
payload = f"{url}|{exp}".encode()
sig = base64.urlsafe_b64encode(hmac.new(SECRET, payload, sha256).digest()).decode()
return f"{url}?" + urlencode({"exp": exp, "sig": sig})




def verify_signature(url: str, exp: int, sig: str) -> bool:
if exp < int(time.time()):
return False
payload = f"{url}|{exp}".encode()
expected = base64.urlsafe_b64encode(hmac.new(SECRET, payload, sha256).digest()).decode()
return hmac.compare_digest(expected, sig)