import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import ngrok

# Force UTF-8 on Windows stdout if possible
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

backend_env = Path(__file__).resolve().parent / ".env"
root_env = Path(__file__).resolve().parent.parent / ".env"

if backend_env.exists():
    load_dotenv(dotenv_path=backend_env)
if root_env.exists():
    load_dotenv(dotenv_path=root_env)

async def start_ngrok():
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    domain = os.getenv("NGROK_DOMAIN", "alongside-vagueness-unfitted.ngrok-free.dev")

    kwargs = {
        "addr": 8000,
    }
    if authtoken:
        kwargs["authtoken"] = authtoken
    else:
        kwargs["authtoken_from_env"] = True

    if domain:
        kwargs["domain"] = domain

    print(f"Connecting ngrok forwarder to port 8000 (Domain: {domain})...")
    
    forwarder = await ngrok.forward(**kwargs)
    public_url = forwarder.url()

    print("=" * 70)
    print(">>> PDFtoDOC API IS NOW PUBLICLY ACCESSIBLE VIA NGROK! <<<")
    print(f">> Public Base URL:     {public_url}")
    print(f">> Interactive Docs:    {public_url}/docs")
    print(f">> Direct Stream API:   {public_url}/api/v1/convert/stream")
    print(f">> Jobs API Endpoint:   {public_url}/api/v1/convert/jobs")
    print(f">> Health Check:        {public_url}/api/v1/health")
    print("=" * 70)
    print("Tunnel is active in background. Keep this process running.")
    sys.stdout.flush()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(start_ngrok())
    except KeyboardInterrupt:
        print("\nTunnel stopped.")
