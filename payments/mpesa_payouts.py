# payments/mpesa_payouts.py
import base64
import requests
import datetime
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

DAR_AJA_ENV = getattr(settings, "MPESA_ENV", "sandbox")

BASE_URL = "https://sandbox.safaricom.co.ke" if DAR_AJA_ENV == "sandbox" else "https://api.safaricom.co.ke"

def get_access_token():
    """
    Use Daraja OAuth token endpoint (client credentials).
    """
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    r.raise_for_status()
    return r.json().get("access_token")

def b2c_payment(phone_number, amount_kes, remarks="Payout", occasion="Payout"):
    """
    Initiate B2C payment to a phone number.
    Returns response JSON.
    NOTE: requires MPESA_B2C_SHORTCODE, MPESA_B2C_INITIATOR, MPESA_B2C_SECURITY_CREDENTIAL, MPESA_B2C_QUEUE_TIMEOUT_URL, MPESA_B2C_RESULT_URL in settings.
    """
    token = get_access_token()
    url = f"{BASE_URL}/mpesa/b2c/v1/paymentrequest"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    payload = {
        "InitiatorName": settings.MPESA_B2C_INITIATOR,
        "SecurityCredential": settings.MPESA_B2C_SECURITY_CREDENTIAL,
        "CommandID": getattr(settings, "MPESA_B2C_COMMAND_ID", "BusinessPayment"),
        "Amount": int(amount_kes),
        "PartyA": settings.MPESA_B2C_SHORTCODE,  # your shortcode
        "PartyB": str(phone_number),  # recipient
        "Remarks": remarks,
        "QueueTimeOutURL": settings.MPESA_B2C_QUEUE_TIMEOUT_URL,
        "ResultURL": settings.MPESA_B2C_RESULT_URL,
        "Occasion": occasion,
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers)
    # do not raise for status automatically; Daraja returns 200 with JSON containing ResponseCode
    try:
        data = r.json()
    except Exception:
        logger.exception("Invalid JSON from MPESA B2C endpoint")
        r.raise_for_status()
        data = {}

    return {"status_code": r.status_code, "response": data}
