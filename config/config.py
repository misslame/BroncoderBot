from dotenv import load_dotenv
import os

load_dotenv()

LEETCODE_USERNAME = os.environ.get("LEETCODE_USERNAME")
LEETCODE_PASSWORD = os.environ.get("LEETCODE_PASSWORD")

LEETCODE_SESSION = os.environ.get("LEETCODE_SESSION")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
