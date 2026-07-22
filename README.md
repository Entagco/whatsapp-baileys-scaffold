# whatsapp-baileys-scaffold

A minimal, working pattern for receiving and sending WhatsApp messages from a
Python backend via a [Baileys](https://github.com/WhiskeySockets/Baileys)
bridge.

WhatsApp doesn't offer a straightforward way for a personal/business number
to receive and send messages programmatically without going through the
official (and comparatively heavy) Cloud API onboarding. A common workaround
is to run Baileys — a Node.js library that speaks the WhatsApp Web protocol —
as a small standalone bridge service, and have your actual application
backend talk to that bridge over a simple internal HTTP API. This repo is the
Python side of that pattern: a FastAPI webhook that receives messages from
the bridge, and a client for sending replies back through it.

This is deliberately small. It does not include:
- The Baileys bridge itself (you run that as its own Node.js service)
- Any message parsing, NLP, or business logic — that's `handle_message` in
  `main.py`, which is a one-line echo you're meant to replace
- Message queuing, retries, or persistence

## How it fits together

```
WhatsApp <-> Baileys bridge (Node.js) <-> this backend (Python/FastAPI)
```

1. Someone sends a WhatsApp message to your bridge's number.
2. The bridge POSTs it to `POST /webhook/message` on this backend, with a
   shared-secret header.
3. This backend calls `handle_message(...)` — replace this with your logic.
4. Your logic (or the default echo) replies via `WhatsAppClient.send()`,
   which POSTs to the bridge's `/send` endpoint.

Auth between the bridge and this backend is a single shared secret checked on
every request (`x-internal-secret` header). This is **not** WhatsApp/Meta
signature verification — it only protects the internal hop between your
bridge and this backend. Run both services on a private network, or put
your own auth in front, if you're exposing this backend publicly.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env with your own INTERNAL_SECRET and BAILEYS_URL
```

## Quick start

```bash
uvicorn main:app --reload --port 8000
```

Then, from your Baileys bridge (or with curl, to simulate it):

```bash
curl -X POST http://localhost:8000/webhook/message \
  -H "Content-Type: application/json" \
  -H "x-internal-secret: your_shared_secret_here" \
  -d '{"sender": "1XXXXXXXXXX@s.whatsapp.net", "body": "hello"}'
```

With `DRY_RUN=true` in your `.env`, replies are printed to stdout instead of
sent through the bridge — useful for local development without a live
WhatsApp session.

To build actual behavior, edit `handle_message()` in `main.py`:

```python
def handle_message(sender: str, body: str, message_id: str = "", timestamp: int = 0) -> None:
    # your logic here
    wa.send(sender, "your reply")
```

## Configuration

All configuration is via environment variables — see [`.env.example`](.env.example):

| Variable          | Description                                              |
|-------------------|------------------------------------------------------------|
| `BAILEYS_URL`     | Base URL of your Baileys bridge service                    |
| `INTERNAL_SECRET` | Shared secret checked on both the webhook and outbound send |
| `DRY_RUN`         | If `true`, messages are logged instead of actually sent     |

## License

MIT — see [LICENSE](LICENSE).

---

Built and maintained by [Entag](https://entag.co), an on-demand manufacturing platform for Egypt and the Middle East.
