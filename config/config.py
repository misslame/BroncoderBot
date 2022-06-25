from dotenv import load_dotenv
import os


load_dotenv()

LEETCODE_USERNAME = os.environ.get("LEETCODE_USERNAME")
LEETCODE_PASSWORD = os.environ.get("LEETCODE_PASSWORD")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
