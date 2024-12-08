from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# Dictionary to store connected users
connected_users = {}

@socketio.on('connect')
def handle_connect():
    print('A user connected.')

@socketio.on('set_username')
def set_username(data):
    connected_users[request.sid] = data['username']
    emit('user_connected', {'username': data['username']}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    username = connected_users.get(request.sid, 'Anonymous')
    message_data = {'username': username, 'message': data}
    emit('message', message_data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = connected_users.pop(request.sid, 'Anonymous')
    emit('user_disconnected', {'username': username}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app ,port=3000, debug=True)
