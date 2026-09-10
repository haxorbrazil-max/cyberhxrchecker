import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN")
ADMIN_ID=int(os.getenv("ADMIN_ID","0"))
PLUSPIX_CLIENT_ID=os.getenv("PLUSPIX_CLIENT_ID")
PLUSPIX_CLIENT_SECRET=os.getenv("PLUSPIX_CLIENT_SECRET")
DATABASE_PATH=os.getenv("DATABASE_PATH","store.db")
if not BOT_TOKEN or not ADMIN_ID: raise RuntimeError("Configure BOT_TOKEN e ADMIN_ID.")
