from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
MONGODB_ID = os.environ.get("MONGODB_ID")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGO_DB_NAME = "gitlio"

MONGODB_URL = f"mongodb+srv://{MONGODB_ID}:{MONGODB_PASSWORD}@gitlio.tx0qdtk.mongodb.net/?retryWrites=true&w=majority&appName=gitlio"

client = MongoClient(MONGODB_URL)
mongo_db = client[MONGO_DB_NAME]
portfolios_collection = mongo_db["portfolios"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)