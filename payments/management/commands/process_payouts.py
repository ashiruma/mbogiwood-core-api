# payments/management/commands/process_payouts.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Payout, PayoutRequest
from payments.mpesa_payouts import b2c_payment
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# threshold: KES 450,000 => cents 45,000,000
AUTO_B2C_THRESHOLD_CENTS = int(getattr(settings, "AUTO_B2C_THRESHOLD_CENTS", 45000000))
MIN_PAYOUT_CENTS = int(getattr(settings, "PAYOUT_MIN_CENTS", 1000000))  # e.g. default 10,000 KES = 1,000,000 cents

class Command(BaseCommand):
    help = "Process pending payouts: auto B2C for amounts below threshold"

    def handle(self, *args, **options):
        pending = Payout.objects.filter(status=Payout.Status.PENDING).order_by("created_at")
        count = 0
        for p in pending:
            try:
                # skip payouts too small or negative
                if p.amount_cents < MIN_PAYOUT_CENTS:
                    logger.info("Skipping payout %s - below minimum", p.id)
                    continue

                # if less than threshold, attempt B2C
                if p.amount_cents <= AUTO_B2C_THRESHOLD_CENTS:
                    # convert cents -> KES
                    amount_kes = p.amount_cents // 100
                    phone = getattr(p.filmmaker, "mpesa_phone_number", None) or getattr(p.filmmaker, "phone_number", None)
                    if not phone:
                        logger.warning("No phone for filmmaker %s; skipping payout %s", p.filmmaker_id, p.id)
                        continue

                    result = b2c_payment(phone, amount_kes, remarks=f"Payout #{p.id}", occasion="FilmmakerPayout")
                    # Inspect result for response content
                    resp = result.get("response", {})
                    if result.get("status_code") == 200 and ("ResponseCode" in resp and str(resp.get("ResponseCode")) == "0"):
                        p.status = Payout.Status.SUCCESS
                        p.completed_at = timezone.now()
                        # store transaction id if present (e.g., ConversationID)
                        conv = resp.get("ConversationID") or resp.get("TransactionID")
                        if conv:
                            p.transaction_id = conv
                        p.save(update_fields=["status", "completed_at", "transaction_id"])
                        count += 1
                    else:
                        # mark as failed or leave pending for manual review
                        logger.warning("B2C failed for payout %s: %s", p.id, resp)
                        # Optionally mark failed:
                        p.status = Payout.Status.FAILED
                        p.save(update_fields=["status"])
                else:
                    # large payout - leave for manual/bank processing
                    logger.info("Payout %s >= threshold; left for manual processing", p.id)
            except Exception as e:
                logger.exception("Error processing payout %s", p.id)
        self.stdout.write(self.style.SUCCESS(f"Processed payouts, auto-paid: {count}"))
