from datetime import datetime, timedelta
import random
from pymongo import MongoClient
client = MongoClient()

db = client.beesite

stats=db.stats
posts=db.posts
users=db.users
topics = db.topics

def remove_stat():
    dt = datetime.utcnow() - timedelta(seconds=604800)
    stats.delete_one({"ts": {"$lt": dt}})

def add_stat(players, mode):
    remove_stat()
    stats.insert_one({"ts": datetime.utcnow(), "players": players, "mode": mode})

def get_daily_stats():
    return [i for i in stats.find().sort("ts", -1).limit(144)][::-1]

def get_weekly_stats():
    return [i for i in stats.find().sort("ts", 1).limit(1008)][0::7]









def add_topic(title,description):
    topics.insert_one({"id":topics.count()+1,"title":title,"description":description,"ts":datetime.utcnow()})

def get_topics():
    return topics.find({}).sort("ts", 1)

def get_topic(topic):
    return topics.find_one({"id": topic})


def find_post_id():
    return [i for i in posts.find().sort("id", -1).limit(1)][0]["id"]+1

def add_post(title,author,authorid,content,origin,topic):
    id = find_post_id()
    posts.insert_one({"pinned": False, "id":id,"author": author,"authorid": authorid,"title":title, "content": content, "origin": origin, "topic": topic, "ts": datetime.utcnow(), "upvotes": [], "views": []})
    return id
def get_posts_for_topic(topic):
    return posts.find({"topic": topic, "origin": None}).sort([["pinned", -1],["ts", -1]])

def get_replies_for_post(post):
    return posts.find({"origin": post}).sort("ts", 1)

def get_topic_post_count(topic):
    if topic == 0:
        return posts.find({}).count()
    else:
        return posts.find({"topic": topic}).count()



def get_full_post(id):
    return {"post": posts.find_one({"id":id}), "replies": get_replies_for_post(id)}


def get_post(id):
    return posts.find_one({"id":id})


def move_thread(id,topic):
    posts.update({"id": id}, {"$set": {"topic": topic}})
    posts.update_many({"origin": id}, {"$set": {"topic": topic}})

def get_post_reply_count(post):
    return posts.find({"origin": post}).count()


def add_user(username,password,email):
    users.insert_one({"ckey": None, "username":username,"password":password,"email":email,"id":users.count()+1,"score": 0,"admin": False, "avatar": None,"ts": datetime.utcnow()})

def get_leaders(sort):
    if sort == "love":
        return users.find({}).sort("score", -1).limit(50)

def get_users():
    return users.find({})

def get_usernames():
    return [u["username"] for u in get_users()]

def get_user(id):
    return users.find_one({"id": id})

def get_user_from_username(username):
    return users.find_one({"username":username})

def get_user_from_email(email):
    return users.find_one({"email": email})

def update_user(user,key,value):
    users.update({"id": user}, {"$set": {key: value}})

def inc_user(user,key,value):
    users.update({"id": user}, {"$inc": {key: value}})


def update_post(post,key,value):
    posts.update({"id": post}, {"$set": {key: value}})

def inc_post(post,key,value):
    posts.update({"id": post}, {"$inc": {key: value}})

def push_post(post,key,value):
    posts.update({"id": post}, {"$push": {key: value}})

def pull_post(post,key,value):
    posts.update({"id": post}, {"$pull": {key: value}})

def delete_post(post):
    posts.delete_one({"id": post})
    posts.delete_many({"origin": post})
