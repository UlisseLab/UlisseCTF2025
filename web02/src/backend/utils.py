from flask_pymongo import PyMongo
import os

def init_db(mongo: PyMongo):
    admin_password = os.urandom(16).hex()
    FLAG1 = os.getenv('FLAG1')
    
    mongo.db.users.update_one(
        {'username': 'administrator'},
        {'$set': {'username': 'administrator', 'password': admin_password}},
        upsert=True
    )
    
    admin_user = mongo.db.users.find_one({'username': 'administrator'})
    admin_id = admin_user['_id']
    
    mongo.db.balances.update_one(
        {'_id': admin_id},
        {'$set': {'amount': 0}},
        upsert=True
    )
    
    mongo.db.transactions.update_one(
        {'_id': admin_id},
        {'$set': {'sender_id': admin_id, 'sender': 'administrator', 'receiver_id': admin_id, 'receiver': 'administrator', 'amount': 0, 'note': FLAG1, 'status': 'success'}},
        upsert=True
    )
    
    print(f"Admin password: {admin_password}", flush=True)
