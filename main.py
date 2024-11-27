from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from Crypto.Cipher import AES
import os
from stem.control import Controller

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
socketio = SocketIO(app)

# In-memory storage for simplicity
active_users = {}

# Encryption setup
def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return nonce + ciphertext

def decrypt_message(key, encrypted):
    nonce = encrypted[:16]
    ciphertext = encrypted[16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ciphertext).decode()

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on('message')
def handle_message(data):
    key = active_users.get(request.sid)  # User's encryption key
    encrypted_message = encrypt_message(key, data['message'])
    emit('message', {'message': encrypted_message}, broadcast=True)

@socketio.on('auth')
def handle_auth(data):
    key = os.urandom(16)  # Generate a unique encryption key per session
    active_users[request.sid] = key
    emit('auth_success', {'key': key.hex()})

if __name__ == "__main__":
    app.run(port=5000)
