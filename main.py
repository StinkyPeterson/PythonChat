from flask import Flask, request, jsonify, render_template, redirect
from datetime import datetime
import logging

app = Flask(__name__, static_folder="./client", template_folder="./client")

# message data
messages = []
message_id = 1

# user data
users = {}
user_id = 1



def get_user_last_seen(user):
    return users[user]['last_seen'] if user in users else None

def update_user_last_seen(user):
    global user_id
    if user not in users:
        users[user] = {'id': user_id, 'last_seen': datetime.now()}
        user_id += 1
        
    return get_user_last_seen(user)

def add_message(sender, text):
    global message_id
    message = {'id': message_id, 'sender': sender, 'text': text, 'time': datetime.now()}
    message_id += 1
    messages.append(message)
    
    messages_file = file = open('mesages.txt', 'a')
    messages_file.write(f"{message['time']} - {message['sender']}: {message['text']}\n")
    messages_file.close()
    return message


# routes
@app.route('/')
def index():
    return redirect("/chat")

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/get_messages')
def get_messages():
    sender = request.args.get('sender')
    user_last_seen = get_user_last_seen(sender)

    if user_last_seen is None:
        user_last_seen = update_user_last_seen(sender)

    result = [message for message in messages if message['time'] >= user_last_seen]
    if result:
        update_user_last_seen(sender)

    return jsonify({'messages': result})

@app.route('/get_users')
def get_users():
    return jsonify(list(users.keys()))

@app.route('/send_message')
def send_message():
    sender = request.args.get('sender')
    text = request.args.get('text')
    message = add_message(sender, text)
    return jsonify({'result': True, 'message': message})
    
@app.route('/delete_message')
def delete_message():
    id = int(request.args.get('id'))
    
    for i in range(len(messages)):
        
        if int(messages[i]["id"]) == id:
            del messages[i]
            break
            
    return jsonify({'result': True})

@app.route('/logout')
def logout():
    sender = request.args.get('sender')

    if sender in users:
        del users[sender]
    
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run()
