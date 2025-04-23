from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from models import Transaction, Result
from ctypes import *
from utils import init_db
from multiprocessing import Process
import os, jwt

app = Flask(__name__)
app.config['MONGO_HOST'] = os.getenv('MONGO_HOST', 'mongodb')
app.config['MONGO_USER'] = os.getenv('MONGO_INITDB_ROOT_USERNAME', 'admin')
app.config['MONGO_PASS'] = os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'password')
app.config['MONGO_DB'] = os.getenv('MONGO_INITDB_DATABASE', 'stackbank')
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'secret')

ADMIN_KEY = os.urandom(8).hex()
FLAG2 = os.getenv('FLAG2')

app.config['MONGO_URI'] = f"mongodb://{app.config['MONGO_USER']}:{app.config['MONGO_PASS']}@{app.config['MONGO_HOST']}:27017/{app.config['MONGO_DB']}?authSource=admin"
mongo = PyMongo(app)
init_db(mongo)

functions = CDLL('./libackend.so')
functions.handle_transaction.argtypes = [Transaction]
functions.handle_transaction.restype = Result
print(f"ADMIN_KEY: {ADMIN_KEY}", flush=True)

def handle_queue():
    transactions = mongo.db.transactions.find({'status': 'pending'})
    q = {}
    for t in transactions:
        if t['sender_id'] not in q:
            q[t['sender_id']] = []
        try:
            amount = int(t['amount'])
            balance = int(mongo.db.balances.find_one({'_id': ObjectId(t['sender_id'])})['amount'])
        except:
            mongo.db.transactions.update_one({'_id': ObjectId(t['_id'])}, {'$set': {'status': 'error'}})        
            continue
        trans = Transaction(
            sender_balance=c_int64(balance), 
            amount=c_int64(amount), 
            note=c_char_p(t['note'].encode()), 
            id=t['_id'],
        )
        q[t['sender_id']].append(trans)
    
    print(f'Found {len(q)} transactions to process', flush=True)
    for sender in q.keys():
        for trans in q[sender]:
            prc = Process(target=handle_transaction, args=(trans, ))
            prc.start()
            prc.join()
            
            if prc.exitcode != 0:
                mongo.db.transactions.update_one({'_id': ObjectId(trans.id)}, {'$set': {'status': 'error'}})        
            del trans
    

def handle_transaction(transactions: Transaction):
    id = transactions.id
    t = mongo.db.transactions.find_one({'_id': ObjectId(id)})
    sender_id, receiver_id, amount = t['sender_id'], t['receiver_id'], t['amount']
    
    print(f'Started transaction {id} from {t["sender"]} to {t["receiver"]} of amount {amount}', flush=True)
    print(transactions.note)
    result = functions.handle_transaction(transactions, c_char_p(ADMIN_KEY.encode()))

    mongo.db.balances.update_one({'_id': ObjectId(sender_id)}, {'$inc': {'amount': -amount}})
    mongo.db.balances.update_one({'_id': ObjectId(receiver_id)}, {'$inc': {'amount': amount}})
    print(result.note, result.status, flush=True)
    mongo.db.transactions.update_one({'_id': ObjectId(id)}, {'$set': {'status': result.status.decode(), 'note': result.note.decode()}})        
    
    del result # free the memory allocated in the library (without this python will give a segmentation fault)

sched = BackgroundScheduler(daemon=False)
sched.add_job(handle_queue, 'interval', seconds=10)
sched.start()

def login_required(f):
    def wrapper(*args, **kwargs):
        session = request.cookies.get('session')
        if not session:
            return jsonify({'error': 'Session not valid'}), 401
        
        try:
            session = jwt.decode(session, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Invalid session cookie'}), 401
        
        if not (user := session['username']):
            return jsonify({'error': 'Username not valid'}), 401

        res = mongo.db.users.find_one({'username': user})
        if not res:
            return jsonify({'error': 'Username not valid'}), 401

        return f((ObjectId(session['id']), session['username']), *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/transaction', methods=['POST'])
@login_required
def transaction(user):
    balance = mongo.db.balances.find_one({'_id': user[0]})['amount']
    
    sender_id = user[0]
    receiver = request.json['receiver']
    amount = request.json['amount']
    note = request.json['note']
    
    if not (receiver := mongo.db.users.find_one({'username': receiver})):
        return jsonify({'error': 'receiver not found'}), 400
    
    receiver_id = receiver['_id']
    if sender_id == receiver_id:
        return jsonify({'error': 'Sender and receiver cannot be the same'}), 400
    
    if balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than 0'}), 400
    
    if receiver['username'] == 'administrator':
        return invest(user)
    
    mongo.db.transactions.insert_one({
        'sender_id': sender_id,
        'sender': user[1],
        'receiver_id': receiver_id,
        'receiver': receiver['username'],
        'amount': amount,
        'note': note,
        'status': 'pending'
    })

    return jsonify({'message': 'Transaction added to queue'}), 200

# No longer needed...
# @app.route('/invest', methods=['POST'])
# @login_required
def invest(user):
    amount = request.json['amount']
    note = request.json['note']
     
    mongo.db.balances.update_one(
        {"user_id": user[0]},
        {"$inc": {"amount": -amount}}
    )
    
    mongo.db.transactions.insert_one({
        'sender_id': user[0],
        'sender': user[1],
        'receiver_id': mongo.db.users.find_one({'username': 'administrator'})['_id'],
        'receiver': 'administrator',
        'amount': amount,
        'note': note,
        'status': 'success'
    })
    
    return jsonify({'message': 'Investment added'}), 200


@app.route('/admin', methods=['GET'])
@login_required
def admin(user):
    balance = mongo.db.balances.find_one({'_id': user[0]})['amount']
    auth = request.args.get('auth')
    if auth != ADMIN_KEY:
        return jsonify({'error': 'Invalid admin key'}), 401
    if balance >= 10000:
        mongo.db.balances.update_one({'_id': user[0]}, {'$set': {'amount': 0}})
        return jsonify({'flag': FLAG2}), 200
    else:
        return jsonify({'error': 'Not enough money to become admin'}), 401