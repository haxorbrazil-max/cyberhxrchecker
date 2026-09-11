import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN=os.getenv("8722077591:AAE9lAawFUJLgdkjas4h2TW8NBdvqK6cR-c")
ADMIN_ID=int(os.getenv("8700038584","0"))
PLUSPIX_-+CLIENT_ID=os.getenv("live_54cdff65c7fe0aae7a614a68d1357792")
PLUSPIX_CLIENT_SECRET=os.getenv("sk_2827fb6ca3db9b29dd5a2c992e7d0743abcef05d980efd3c36d0e8e2f7c2f661")
DATABASE_PATH=os.getenv("DATABASE_PATH","store.db")
if not BOT_TOKEN or not ADMIN_ID: raise RuntimeError("8722077591:AAG3c-pPxfe4Km2N8HdXsYGeA12UGH7inB0","8700038584")
