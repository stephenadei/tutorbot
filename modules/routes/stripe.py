from __future__ import annotations

from flask import Flask, request
from modules.handlers.payment import verify_stripe_webhook, handle_payment_success, add_payment_note
from modules.utils.cw_api import add_conv_labels, remove_conv_labels, set_conv_attrs


def register(app: Flask) -> None:
    @app.post("/webhook/payments")
    def stripe_webhook():
        payload = request.get_data()
        signature = request.headers.get('Stripe-Signature')

        if not verify_stripe_webhook(payload, signature):
            return "Unauthorized", 401

        event = request.get_json()
        event_type = event.get("type")

        if event_type in ("checkout.session.completed", "payment_intent.succeeded"):
            handle_payment_success(event)
            try:
                obj = event.get("data", {}).get("object", {})
                metadata = obj.get("metadata", {})
                conversation_id = metadata.get("chatwoot_conversation_id") or metadata.get("conversation_id")
                amount = obj.get("amount_total") or obj.get("amount") or 0
                currency = obj.get("currency", "eur")
                order_id = metadata.get("order_id")
                if conversation_id:
                    remove_conv_labels(conversation_id, ["status:awaiting_pay"])  # type: ignore[arg-type]
                    add_conv_labels(conversation_id, ["payment:paid", "status:booked"])  # type: ignore[arg-type]
                    set_conv_attrs(conversation_id, {"payment_status": "paid"})  # type: ignore[arg-type]
                    add_payment_note(str(conversation_id), int(amount), currency, order_id)
            except Exception:
                pass

        return "OK", 200




