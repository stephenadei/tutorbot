from __future__ import annotations

from flask import Flask


def register(app: Flask) -> None:
    @app.route("/health")
    def health():
        return {"status": "healthy", "service": "tutorbot"}, 200




