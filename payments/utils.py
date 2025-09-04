# payments/utils.py
import requests, base64
from django.conf import settings
from datetime import datetime
from requests.auth import HTTPBasicAuth


def mpesa_b2c_payout(phone_number, amount, remarks="Filmmaker Payout"):
    """
    Initiate an M-Pesa B2C Payout request.
    Note: This requires B2C API credentials and permissions from Safaricom.
    """
    token = get_mpesa_token()
    
    payload = {
        "OriginatorConversationID": "some_unique_id_here", # You'll need to generate a unique ID
        "InitiatorName": settings.MPESA_B2C_INITIATOR_NAME,
        "SecurityCredential": settings.MPESA_B2C_SECURITY_CREDENTIAL, # This is generated from your live cert
        "CommandID": "BusinessPayment",
        "Amount": str(int(amount)),
        "PartyA": settings.MPESA_SHORTCODE,
        "PartyB": str(phone_number),
        "Remarks": remarks,
        "QueueTimeOutURL": settings.MPESA_B2C_TIMEOUT_URL,
        "ResultURL": settings.MPESA_B2C_RESULT_URL,
        "Occassion": "Filmmaker Payment"
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{settings.MPESA_BASE_URL}/mpesa/b2c/v1/paymentrequest"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    
def get_mpesa_token():
    """Request OAuth token from Safaricom"""
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        timeout=10
    )
    response.raise_for_status()
    return response.json().get("access_token")


def generate_password(timestamp):
    """Generate base64-encoded password: Shortcode + Passkey + Timestamp"""
    data_to_encode = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(data_to_encode.encode()).decode()


def stk_push(phone, amount, account_reference="MBOGIWOOD", transaction_desc="Film Payment"):
    """Initiate M-Pesa STK Push request"""
    token = get_mpesa_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = generate_password(timestamp)

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(int(amount)),  # must be string/int, not decimal
        "PartyA": str(phone),
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": str(phone),
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
