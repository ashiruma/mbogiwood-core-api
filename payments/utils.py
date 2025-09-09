import base64
import datetime
import json
import logging
import subprocess
import uuid

import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

logger = logging.getLogger(__name__)

# Settings keys (expected in settings / .env)
MPESA_BASE_URL = getattr(settings, "MPESA_BASE_URL", "https://sandbox.safaricom.co.ke")
MPESA_CONSUMER_KEY = getattr(settings, "MPESA_CONSUMER_KEY", None)
MPESA_CONSUMER_SECRET = getattr(settings, "MPESA_CONSUMER_SECRET", None)
MPESA_SHORTCODE = getattr(settings, "MPESA_SHORTCODE", None)
MPESA_PASSKEY = getattr(settings, "MPESA_PASSKEY", None)
MPESA_CALLBACK_URL = getattr(settings, "MPESA_CALLBACK_URL", None)

# B2C settings
MPESA_B2C_INITIATOR_NAME = getattr(settings, "MPESA_B2C_INITIATOR_NAME", None)
# Preferred: set MPESA_B2C_SECURITY_CREDENTIAL in env (pre-encrypted). If not provided, code can attempt to use cert to encrypt.
MPESA_B2C_SECURITY_CREDENTIAL = getattr(settings, "MPESA_B2C_SECURITY_CREDENTIAL", None)
MPESA_B2C_SHORTCODE = getattr(settings, "MPESA_B2C_SHORTCODE", MPESA_SHORTCODE)
MPESA_B2C_TIMEOUT_URL = getattr(settings, "MPESA_B2C_TIMEOUT_URL", None)
MPESA_B2C_RESULT_URL = getattr(settings, "MPESA_B2C_RESULT_URL", None)
MPESA_B2C_CERT_PATH = getattr(settings, "MPESA_B2C_CERT_PATH", None)  # optional path to Safaricom public cert for encryption


def _http_get_token():
    """
    Obtain Daraja OAuth token using HTTP Basic Auth.
    Returns access_token string or raises requests.HTTPError.
    """
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    resp = requests.get(url, auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("No access_token in Daraja response: %s" % (json.dumps(data)))
    return token


def _generate_stk_password(timestamp: str) -> str:
    """
    STK Push password = base64(Shortcode + Passkey + Timestamp)
    """
    raw = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


def _ensure_security_credential():
    """
    Return a SecurityCredential for B2C calls.
    Preferred flow: set MPESA_B2C_SECURITY_CREDENTIAL in settings (pre-generated).
    Fallback: if MPESA_B2C_CERT_PATH and MPESA_B2C_INITIATOR_PASSWORD are present, attempt to encrypt using openssl.
    If neither available -> raise error (Daraja requires SecurityCredential).
    """
    if MPESA_B2C_SECURITY_CREDENTIAL:
        return MPESA_B2C_SECURITY_CREDENTIAL

    # Attempt to encrypt using cert + openssl if provided
    initiator_password = getattr(settings, "MPESA_B2C_INITIATOR_PASSWORD", None)
    cert_path = MPESA_B2C_CERT_PATH
    if not initiator_password or not cert_path:
        raise RuntimeError(
            "B2C SecurityCredential not found. Set MPESA_B2C_SECURITY_CREDENTIAL in settings or provide MPESA_B2C_CERT_PATH and MPESA_B2C_INITIATOR_PASSWORD."
        )

    # Use openssl to encrypt: echo -n password | openssl rsautl -encrypt -pubin -inkey cert.pem | base64
    try:
        p1 = subprocess.Popen(
            ["echo", "-n", initiator_password], stdout=subprocess.PIPE
        )
        p2 = subprocess.Popen(
            ["openssl", "rsautl", "-encrypt", "-pubin", "-inkey", cert_path],
            stdin=p1.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p1.stdout.close()
        out, err = p2.communicate(timeout=15)
        if p2.returncode != 0:
            raise RuntimeError(f"OpenSSL failed: {err.decode().strip()}")
        # base64 already produced by openssl? We ensure base64 encoding
        sec = base64.b64encode(out).decode()
        return sec
    except Exception as e:
        logger.exception("Failed to generate SecurityCredential using openssl")
        raise


# -------------------------
# STK Push (Customer -> Business)
# -------------------------
def stk_push(phone_number, amount, account_reference="MBOGIWOOD", transaction_desc="Film payment"):
    """
    Initiate STK push. `amount` is expected as integer KES (not cents).
    Returns parsed JSON response from Daraja or raises requests.HTTPError.
    """
    if not all([MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_SHORTCODE, MPESA_PASSKEY, MPESA_CALLBACK_URL]):
        raise RuntimeError("Missing MPesa configuration. Check MPESA_* settings in env.")

    token = _http_get_token()
    timestamp = datetime.datetime.datetime.now().strftime("%Y%m%d%H%M%S") if hasattr(datetime, 'datetime') else datetime.now().strftime("%Y%m%d%H%M%S")
    # ensure timestamp variable is string; above handles both import styles
    # use robust timestamp:
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    password = _generate_stk_password(timestamp)

    url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": str(phone_number),
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": str(phone_number),
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    # Do not raise automatically — caller may want to handle Daraja errors; still raise for network errors
    try:
        resp.raise_for_status()
    except Exception:
        logger.exception("STK push HTTP error: %s", resp.text)
        raise
    return resp.json()


# -------------------------
# B2C Payment (Business -> Customer) - named b2c_payment for views compatibility
# -------------------------
def b2c_payment(phone_number, amount, remarks="Filmmaker payout", originator_id=None):
    """
    Initiate a Business->Customer (B2C) payout.
    - phone_number: in format 2547XXXXXXXX
    - amount: integer KES (not cents)
    Returns Daraja response JSON.
    """
    if not all([MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_B2C_INITIATOR_NAME, MPESA_B2C_SHORTCODE, MPESA_B2C_RESULT_URL, MPESA_B2C_TIMEOUT_URL]):
        raise RuntimeError("Missing B2C configuration in settings. Check MPESA_B2C_* env values.")

    token = _http_get_token()
    url = f"{MPESA_BASE_URL}/mpesa/b2c/v1/paymentrequest"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    security_credential = _ensure_security_credential()

    # create a unique OriginatorConversationID if one wasn't provided
    originator_conv = originator_id or str(uuid.uuid4())

    payload = {
        "InitiatorName": MPESA_B2C_INITIATOR_NAME,
        "SecurityCredential": security_credential,
        "CommandID": "BusinessPayment",
        "Amount": int(amount),
        "PartyA": MPESA_B2C_SHORTCODE,
        "PartyB": str(phone_number),
        "Remarks": remarks,
        "QueueTimeOutURL": MPESA_B2C_TIMEOUT_URL,
        "ResultURL": MPESA_B2C_RESULT_URL,
        "Occasion": "FilmmakerPayout",
        "OriginatorConversationID": originator_conv,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=20)
    try:
        resp.raise_for_status()
    except Exception:
        logger.exception("B2C HTTP error: %s", resp.text)
        raise
    return resp.json()
