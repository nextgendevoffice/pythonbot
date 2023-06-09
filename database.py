# database.py
from pymongo import MongoClient
from config import MONGODB_CONNECTION_STRING

client = MongoClient(MONGODB_CONNECTION_STRING)
db = client['football_bot']
users = db['users']

def add_user(user_id):
    user = get_user(user_id)
    if not user:
        user = {"_id": user_id, "registered": True}
        users.insert_one(user)
    else:
        users.update_one({"_id": user_id}, {"$set": {"registered": True}})
        
def get_user(user_id):
    return users.find_one({"_id": user_id})

def add_leagues_to_user(user_id, leagues):
    users.update_one({"_id": user_id}, {"$addToSet": {"leagues": {"$each": leagues}}})

def get_followed_leagues(user_id):
    user = users.find_one({"_id": user_id})
    return user.get("leagues", [])

def get_all_users():
    return [user["_id"] for user in users.find({"registered": True})]
