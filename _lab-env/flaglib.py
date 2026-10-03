"""Zajednička flag-funkcija za ISS vježbe.

Flag je jedinstven po studentu: izveden iz studentovog **matičnog broja** i
tajnog nastavnikovog seeda (`ISS_SECRET`). Isti materijal ide svima; student pri
radu upiše svoj matični broj, a meta/alat izračuna njegov flag. Nastavnik iste
flagove dobije jednom naredbom nad popisom (vidi `flaggen/checker.py`).

flag("lab08", "0036512345", secret) -> "ASPIRA{sis_ai_1a2b3c}"
"""
import hashlib
import hmac

# Format po vježbi (zadržan zbog uputa u handoutima, npr. Lab 01 mask napad).
FORMAT = {
    "lab01": "ASPIRA{{sis_{}}}",
    "lab02": "ASPIRA{{sis_crypto_{}}}",
    "lab06": "ASPIRA{{sis06_{}}}",
    "lab07": "ASPIRA{{sis_incident_{}}}",
    "lab08": "ASPIRA{{sis_ai_{}}}",
}


def hex6(lab: str, mb: str, secret: str) -> str:
    """Šest heksadekadskih znakova, HMAC(secret, 'lab:matični_broj')."""
    mac = hmac.new(secret.encode(), f"{lab}:{mb}".encode(), hashlib.sha256)
    return mac.hexdigest()[:6]


def make_flag(lab: str, mb: str, secret: str) -> str:
    return FORMAT[lab].format(hex6(lab, mb, secret))
