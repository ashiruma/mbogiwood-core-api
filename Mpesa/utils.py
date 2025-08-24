# mpesa/utils.py
import base64
import datetime
import requests
from django.conf import settings

def generate_password():
    """
    Generate Mpesa STK password.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    encoded = base64.b64encode(data_to_encode.encode())
    return encoded.decode('utf-8'), timestamp


def get_access_token():
    """
    Generate Mpesa access token using consumer key/secret.
    """
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    response.raise_for_status()
    return response.json().get("access_token")


def stk_push(phone_number: str, amount: int, account_reference: str, transaction_desc: str):
    """
    Initiates STK push.
    """
    password, timestamp = generate_password()
    access_token = get_access_token()

    api_url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
