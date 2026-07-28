#!/usr/bin/env bash
# End-to-end smoke check: boots the stack, exercises HTTP + WS + queue, lints.
# Run from the project root with the compose services already reachable.
set -euo pipefail

docker compose up -d
uv run manage.py migrate
uv run manage.py createsuperuser --noinput || true

# Start uvicorn on the host in the background — runserver doesn't upgrade WS.
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!
uv run manage.py rqworker default &
WORKER_PID=$!

up=""
for i in 1 2 3 4 5; do
  curl -sf http://127.0.0.1:8000/admin/login/ > /dev/null && up=1 && break
  sleep 1
done
[ -n "$up" ] || { echo "BOOT CHECK FAILED: uvicorn never came up"; kill "$UVICORN_PID" "$WORKER_PID"; exit 1; }

curl -sf -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename":"a.png","size":42}' > /dev/null
! curl -sf -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename":"a.png"}' > /dev/null
test "$(curl -sf http://127.0.0.1:8000/healthz)" = "ok"
test "$(curl -sf http://127.0.0.1:8000/readyz)" = "ready"

# WebSocket round-trip via the `websockets` lib (a transitive dep of
# uvicorn[standard]). Connects, sends one message, expects it back.
uv run python -c "
import asyncio, json, websockets

async def main():
    # AllowedHostsOriginValidator requires an Origin header; the Python
    # websockets client doesn't send one by default.
    async with websockets.connect('ws://127.0.0.1:8000/ws/echo/', origin='http://localhost') as ws:
        await ws.send(json.dumps({'text': 'ping'}))
        reply = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        assert reply == {'text': 'ping'}, reply

asyncio.run(main())
"

uv run ruff check .
uv run pyright
kill "$UVICORN_PID" "$WORKER_PID"
echo "SMOKE OK"
