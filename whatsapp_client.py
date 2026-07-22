"""Minimal client for sending WhatsApp messages via a Baileys bridge.

A "Baileys bridge" is a small Node.js service (built on the Baileys library)
that maintains an authenticated WhatsApp Web session and exposes a simple
HTTP API for sending messages. This client talks to that bridge; it does not
talk to WhatsApp directly.

Expects the bridge to expose:
    POST {BAILEYS_URL}/send
        headers: {"x-internal-secret": "<shared secret>"}
        json:    {"to": "<jid>", "message": "<text>"}
        returns: {"message_id": "<id>"}  (any JSON shape is fine, "message_id" is optional)
"""

import os

import requests

BAILEYS_URL = os.environ.get("BAILEYS_URL", "http://localhost:3000")
INTERNAL_SECRET = os.environ.get("INTERNAL_SECRET", "")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"


class WhatsAppClient:
    def send(self, to_jid: str, body: str) -> str:
        """
        Send a WhatsApp message via the Baileys bridge.

        to_jid: Baileys JID format, e.g. "1XXXXXXXXXX@s.whatsapp.net"
        Returns the message_id from the bridge, or "DRY-RUN" if DRY_RUN=true.
        """
        if DRY_RUN:
            print(f"[DRY RUN] WhatsApp -> {to_jid}:\n{body}\n")
            return "DRY-RUN"

        resp = requests.post(
            f"{BAILEYS_URL}/send",
            json={"to": to_jid, "message": body},
            headers={"x-internal-secret": INTERNAL_SECRET},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("message_id", "")
