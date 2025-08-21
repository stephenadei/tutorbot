from __future__ import annotations

from flask import Flask, request
from modules.handlers.webhook import verify_webhook, process_webhook


def register(app: Flask) -> None:
    @app.post("/cw")
    def cw():
        if not verify_webhook(request):
            return "Unauthorized", 401
        data = request.get_json()
        try:
            result = process_webhook(data)
            return result, 200
        except Exception as exc:
            print(f"❌ Error processing webhook: {exc}")
            return "Internal Server Error", 500




