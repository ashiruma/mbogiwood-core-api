# Minimal interface. Replace with Daraja/Paybill/B2C integration.


def send_mpesa_payout(phone_number: str, amount_cents: int) -> dict:
# Convert to KES and call real API here.
# Return a structure with transaction reference and status.
return {"status": "PAID", "reference": "MPESA-TEST-REF"}