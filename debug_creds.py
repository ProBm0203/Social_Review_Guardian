# debug_creds.py
import os
from dotenv import load_dotenv

load_dotenv(override=True)

user = os.getenv("GMAIL_USER")
pwd = os.getenv("GMAIL_APP_PASSWORD")

print(f"Loaded GMAIL_USER: '{user}'")
print(f"Loaded GMAIL_APP_PASSWORD: " + (f"'{pwd}'" if pwd else "None"))
if pwd:
    print(f"Password length: {len(pwd)}")
    print(f"Contains spaces: {' ' in pwd}")
