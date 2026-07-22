"""FastAPI webhook for incoming WhatsApp messages from a Baileys bridge.

This is a minimal, working scaffold: it receives a parsed message from your
Baileys bridge, authenticates the request with a shared secret, and hands the
message off to `handle_message` below. Replace `handle_message` with your
own logic — parse the text, call an LLM, look something up, whatever your
bot needs to do.
"""

import os
import traceback

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from whatsapp_client import WhatsAppClient

INTERNAL_SECRET = os.environ.get("INTERNAL_SECRET", "")

app = FastAPI(title="WhatsApp Baileys Scaffold")
wa = WhatsAppClient()


class IncomingMessage(BaseModel):
    sender: str       # Baileys JID, e.g. "1XXXXXXXXXX@s.whatsapp.net"
    body: str
    message_id: str = ""
    timestamp: int = 0


@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/webhook/message")
async def whatsapp_webhook(
    msg: IncomingMessage,
    x_internal_secret: str = Header(default=""),
):
    """Entry point your Baileys bridge should POST incoming messages to.

    Auth is a simple shared-secret header check — the bridge and this
    service must agree on INTERNAL_SECRET. This is not WhatsApp/Meta
    signature verification; it only protects the internal hop between
    your bridge and this backend, so keep both services on a private
    network or behind your own auth layer.
    """
    if not INTERNAL_SECRET or x_internal_secret != INTERNAL_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        handle_message(sender=msg.sender, body=msg.body, message_id=msg.message_id, timestamp=msg.timestamp)
    except Exception as e:
        traceback.print_exc()
        try:
            wa.send(msg.sender, f"Error handling your message: {str(e)[:100]}")
        except Exception:
            pass

    return {"ok": True}


def handle_message(sender: str, body: str, message_id: str = "", timestamp: int = 0) -> None:
    """EXAMPLE HANDLER — replace this with your own message-handling logic.

    This is where you'd typically:
      1. Decide whether `sender` is allowed to use the bot.
      2. Parse or route `body` (regex, an LLM call, a state machine, etc).
      3. Do whatever work the message triggers (write to a DB, call an API).
      4. Reply via `wa.send(sender, reply_text)`.

    The example below just echoes the message back.
    """
    reply = f"Echo: {body}"
    wa.send(sender, reply)
